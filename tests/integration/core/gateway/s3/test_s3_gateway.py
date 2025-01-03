import asyncio
import io
from datetime import datetime
from unittest import mock

import boto3
import pytest
from botocore.exceptions import ClientError

from src.core.domain.exceptions import DoesNotExist
from src.core.gateway.s3.s3_gateway import S3Gateway
from src.core.gateway.s3.s3_provider import S3BucketOptions, S3BucketProvider
from src.core.repository.base.filter import Filter
from src.core.repository.base.pagination import PageOptions

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def s3_url():
    return "http://0.0.0.0:9000"


@pytest.fixture(scope="module")
def s3_settings(s3_url):
    minio_settings = {
        "url": s3_url,
        "access_key": "jobtracker",
        "secret_key": "jobtracker",
        "bucket": "jobtracker-test",
        "region": None,
    }
    if not minio_settings["bucket"].endswith("-test"):  # type: ignore
        pytest.exit("Not running against a test minio bucket?! 😱")
    return minio_settings.copy()


@pytest.fixture(scope="module")
def s3_bucket(s3_settings):
    s3 = boto3.resource(
        "s3",
        endpoint_url=s3_settings["url"],
        aws_access_key_id=s3_settings["access_key"],
        aws_secret_access_key=s3_settings["secret_key"],
    )
    bucket = s3.Bucket(s3_settings["bucket"])
    try:
        bucket.create()
    except ClientError as e:
        if "BucketAlreadyOwnedByYou" in str(e):
            pass
    return bucket


@pytest.fixture(scope="function")
async def s3_provider(s3_bucket, s3_settings) -> S3BucketProvider:
    # wipe contents before each test
    s3_bucket.objects.all().delete()
    provider = S3BucketProvider(S3BucketOptions(**s3_settings))
    await provider.connect()
    yield provider
    await provider.disconnect()


@pytest.fixture(scope="function")
def s3_gateway(s3_provider) -> S3Gateway:
    return S3Gateway(s3_provider)


@pytest.fixture
def object_in_s3(s3_bucket):
    s3_bucket.upload_fileobj(io.BytesIO(b"foo"), "object-in-s3")
    return "object-in-s3"


@pytest.fixture
def local_file(tmp_path):
    path = tmp_path / "test-upload.txt"
    path.write_bytes(b"foo")
    return path


async def test_upload_file(s3_gateway: S3Gateway, local_file):
    object_name = "test-upload-file"

    await s3_gateway.upload_file(object_name, local_file)

    assert (await s3_gateway.get(object_name))["size"] == 3


async def test_upload_file_does_not_exist(s3_gateway: S3Gateway, tmp_path):
    path = tmp_path / "test-upload.txt"
    object_name = "test-upload-file"

    with pytest.raises(FileNotFoundError):
        await s3_gateway.upload_file(object_name, path)


async def test_download_file(s3_gateway: S3Gateway, local_file, tmp_path):
    path = tmp_path / "test-download.txt"
    await s3_gateway.upload_file("test-download-file", local_file)
    await s3_gateway.download_file("test-download-file", path)

    assert path.read_bytes() == b"foo"


async def test_download_file_path_already_exists(
    s3_gateway: S3Gateway, object_in_s3, tmp_path
):
    path = tmp_path / "test-download.txt"
    path.write_bytes(b"bar")

    with pytest.raises(FileExistsError):
        await s3_gateway.download_file(object_in_s3, path)


async def test_download_file_does_not_exist(s3_gateway: S3Gateway, s3_bucket, tmp_path):
    path = tmp_path / "test-download-does-not-exist.txt"

    with pytest.raises(DoesNotExist):
        await s3_gateway.download_file("some-nonexisting", path)

    assert not path.exists()


async def test_remove(s3_gateway: S3Gateway, s3_bucket):
    obj = "object-remove"

    s3_bucket.upload_fileobj(io.BytesIO(b"foo"), obj)
    await s3_gateway.remove(obj)

    assert await s3_gateway.get(obj) is None


async def test_remove_does_not_exist(s3_gateway: S3Gateway, s3_bucket):
    await s3_gateway.remove("non-existing")


@pytest.fixture
def multiple_objects(s3_bucket):
    s3_bucket.upload_fileobj(io.BytesIO(b"a"), "raster-1/bla")
    s3_bucket.upload_fileobj(io.BytesIO(b"ab"), "raster-2/bla")
    s3_bucket.upload_fileobj(io.BytesIO(b"abc"), "raster-2/foo")
    s3_bucket.upload_fileobj(io.BytesIO(b"abcde"), "raster-2/bz")
    return ["raster-1/bla", "raster-2/bla", "raster-2/foo", "raster-2/bz"]


async def test_remove_multiple(s3_gateway: S3Gateway, multiple_objects):
    await s3_gateway.remove_multiple(multiple_objects[:2])

    for key in multiple_objects[:2]:
        assert await s3_gateway.get(key) is None

    for key in multiple_objects[2:]:
        assert await s3_gateway.get(key) is not None


async def test_remove_multiple_empty_list(s3_gateway: S3Gateway, s3_bucket):
    await s3_gateway.remove_multiple([])


async def test_remove_filtered_all(s3_gateway: S3Gateway, multiple_objects):
    await s3_gateway.remove_filtered([])

    for key in multiple_objects:
        assert await s3_gateway.get(key) is None


async def test_remove_filtered_prefix(s3_gateway: S3Gateway, multiple_objects):
    await s3_gateway.remove_filtered([Filter(field="prefix", values=["raster-2/"])])

    assert await s3_gateway.get(multiple_objects[0]) is not None
    for key in multiple_objects[1:]:
        assert await s3_gateway.get(key) is None


@mock.patch("src.core.gateway.s3.s3_gateway.AWS_LIMIT", new=1)
async def test_remove_filtered_pagination(s3_gateway: S3Gateway, multiple_objects):
    await s3_gateway.remove_filtered([Filter(field="prefix", values=["raster-2/"])])

    assert await s3_gateway.get(multiple_objects[0]) is not None
    for key in multiple_objects[1:]:
        assert await s3_gateway.get(key) is None


async def test_filter(s3_gateway: S3Gateway, multiple_objects):
    actual = await s3_gateway.filter([], params=PageOptions(limit=10))
    assert len(actual) == 4
    assert actual[0]["id"] == "raster-1/bla"
    assert isinstance(actual[0]["last_modified"], datetime)
    assert actual[0]["etag"] == "0cc175b9c0f1b6a831c399e269772661"
    assert actual[0]["size"] == 1


async def test_filter_empty(s3_gateway: S3Gateway, s3_bucket):
    actual = await s3_gateway.filter([], params=PageOptions(limit=10))
    assert actual == []


async def test_filter_with_limit(s3_gateway: S3Gateway, multiple_objects):
    actual = await s3_gateway.filter([], params=PageOptions(limit=2))
    assert len(actual) == 2
    assert actual[0]["id"] == "raster-1/bla"
    assert actual[1]["id"] == "raster-2/bla"


async def test_filter_with_cursor(s3_gateway: S3Gateway, multiple_objects):
    actual = await s3_gateway.filter(
        [], params=PageOptions(limit=3, cursor="raster-2/bla")
    )
    assert len(actual) == 2
    assert actual[0]["id"] == "raster-2/bz"
    assert actual[1]["id"] == "raster-2/foo"


async def test_filter_by_prefix(s3_gateway: S3Gateway, multiple_objects):
    actual = await s3_gateway.filter([Filter(field="prefix", values=["raster-1/"])])
    assert len(actual) == 1

    actual = await s3_gateway.filter([Filter(field="prefix", values=["raster-2/"])])
    assert len(actual) == 3


async def test_get(s3_gateway: S3Gateway, object_in_s3):
    actual = await s3_gateway.get(object_in_s3)
    assert actual["id"] == "object-in-s3"
    assert isinstance(actual["last_modified"], datetime)
    assert actual["etag"] == "acbd18db4cc2f85cedef654fccc4a4d8"
    assert actual["size"] == 3


async def test_get_does_not_exist(s3_gateway: S3Gateway):
    actual = await s3_gateway.get("non-existing")
    assert actual is None
