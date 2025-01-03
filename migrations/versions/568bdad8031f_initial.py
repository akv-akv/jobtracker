"""Initial

Revision ID: 568bdad8031f
Revises:
Create Date: 2024-12-23 14:42:29.137351

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "568bdad8031f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "country",
            sa.Enum(
                "Afghanistan",
                "AlandIslands",
                "Albania",
                "Algeria",
                "AmericanSamoa",
                "Andorra",
                "Angola",
                "Anguilla",
                "Antarctica",
                "AntiguaAndBarbuda",
                "Argentina",
                "Armenia",
                "Aruba",
                "Australia",
                "Austria",
                "Azerbaijan",
                "Bahamas",
                "Bahrain",
                "Bangladesh",
                "Barbados",
                "Belarus",
                "Belgium",
                "Belize",
                "Benin",
                "Bermuda",
                "Bhutan",
                "Bolivia",
                "BosniaAndHerzegovina",
                "Botswana",
                "BouvetIsland",
                "Brazil",
                "BritishIndianOceanTerritory",
                "BritishVirginIslands",
                "Brunei",
                "Bulgaria",
                "BurkinaFaso",
                "Burundi",
                "Cambodia",
                "Cameroon",
                "Canada",
                "CapeVerde",
                "CaribbeanNetherlands",
                "CaymanIslands",
                "CentralAfricanRepublic",
                "Chad",
                "Chile",
                "China",
                "ChristmasIsland",
                "CocosKeelingIslands",
                "Colombia",
                "Comoros",
                "CongoBrazzaville",
                "CongoKinshasa",
                "CookIslands",
                "CostaRica",
                "IvoryCoast",
                "Croatia",
                "Cuba",
                "Curacao",
                "Cyprus",
                "Czechia",
                "Denmark",
                "Djibouti",
                "Dominica",
                "DominicanRepublic",
                "Ecuador",
                "Egypt",
                "ElSalvador",
                "EquatorialGuinea",
                "Eritrea",
                "Estonia",
                "Eswatini",
                "Ethiopia",
                "FalklandIslands",
                "FaroeIslands",
                "Fiji",
                "Finland",
                "France",
                "FrenchGuiana",
                "FrenchPolynesia",
                "FrenchSouthernTerritories",
                "Gabon",
                "Gambia",
                "Georgia",
                "Germany",
                "Ghana",
                "Gibraltar",
                "Greece",
                "Greenland",
                "Grenada",
                "Guadeloupe",
                "Guam",
                "Guatemala",
                "Guernsey",
                "Guinea",
                "GuineaBissau",
                "Guyana",
                "Haiti",
                "HeardAndMcDonaldIslands",
                "Honduras",
                "HongKong",
                "Hungary",
                "Iceland",
                "India",
                "Indonesia",
                "Iran",
                "Iraq",
                "Ireland",
                "IsleOfMan",
                "Israel",
                "Italy",
                "Jamaica",
                "Japan",
                "Jersey",
                "Jordan",
                "Kazakhstan",
                "Kenya",
                "Kiribati",
                "Kuwait",
                "Kyrgyzstan",
                "Laos",
                "Latvia",
                "Lebanon",
                "Lesotho",
                "Liberia",
                "Libya",
                "Liechtenstein",
                "Lithuania",
                "Luxembourg",
                "Macao",
                "Madagascar",
                "Malawi",
                "Malaysia",
                "Maldives",
                "Mali",
                "Malta",
                "MarshallIslands",
                "Martinique",
                "Mauritania",
                "Mauritius",
                "Mayotte",
                "Mexico",
                "Micronesia",
                "Moldova",
                "Monaco",
                "Mongolia",
                "Montenegro",
                "Montserrat",
                "Morocco",
                "Mozambique",
                "Myanmar",
                "Namibia",
                "Nauru",
                "Nepal",
                "Netherlands",
                "NewCaledonia",
                "NewZealand",
                "Nicaragua",
                "Niger",
                "Nigeria",
                "Niue",
                "NorfolkIsland",
                "NorthKorea",
                "NorthMacedonia",
                "NorthernMarianaIslands",
                "Norway",
                "Oman",
                "Pakistan",
                "Palau",
                "PalestinianTerritories",
                "Panama",
                "PapuaNewGuinea",
                "Paraguay",
                "Peru",
                "Philippines",
                "PitcairnIslands",
                "Poland",
                "Portugal",
                "PuertoRico",
                "Qatar",
                "Reunion",
                "Romania",
                "Russia",
                "Rwanda",
                "Samoa",
                "SanMarino",
                "SaoTomeAndPrincipe",
                "SaudiArabia",
                "Senegal",
                "Serbia",
                "Seychelles",
                "SierraLeone",
                "Singapore",
                "SintMaarten",
                "Slovakia",
                "Slovenia",
                "SolomonIslands",
                "Somalia",
                "SouthAfrica",
                "SouthGeorgiaAndSouthSandwichIslands",
                "SouthKorea",
                "SouthSudan",
                "Spain",
                "SriLanka",
                "Sudan",
                "Suriname",
                "SvalbardAndJanMayen",
                "Sweden",
                "Switzerland",
                "Syria",
                "Taiwan",
                "Tajikistan",
                "Tanzania",
                "Thailand",
                "TimorLeste",
                "Togo",
                "Tokelau",
                "Tonga",
                "TrinidadAndTobago",
                "Tunisia",
                "Turkey",
                "Turkmenistan",
                "TurksAndCaicosIslands",
                "Tuvalu",
                "USOutlyingIslands",
                "USVirginIslands",
                "Uganda",
                "Ukraine",
                "UnitedArabEmirates",
                "UnitedKingdom",
                "UnitedStates",
                "Uruguay",
                "Uzbekistan",
                "Vanuatu",
                "VaticanCity",
                "Venezuela",
                "Vietnam",
                "WallisAndFutuna",
                "WesternSahara",
                "Yemen",
                "Zambia",
                "Zimbabwe",
                name="country",
            ),
            nullable=True,
        ),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column(
            "work_setting_type",
            sa.Enum("REMOTE", "HYBRID", "ONSITE", name="worksettingtype"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ADDED",
                "APPLIED",
                "INTERVIEWING",
                "OFFERED",
                "REJECTED",
                "ARCHIVED",
                name="jobstatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "employment_type",
            sa.Enum("FULLTIME", "TEMPORARY", "CONTRACT", name="employmenttype"),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("platform", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("jobs")
    op.drop_table("users")
    # ### end Alembic commands ###
