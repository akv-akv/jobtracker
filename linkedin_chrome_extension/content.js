// Safely query and extract text content
function extractText(selector) {
    try {
        const element = document.querySelector(selector);
        return element ? element.innerText.trim() : "N/A";
    } catch (error) {
        console.error(`Error extracting text for selector: ${selector}`, error);
        return "N/A";
    }
}

// Extract additional job details
function extractAdditionalDetails() {
    const hiddenElements = document.querySelectorAll(".job-details-preferences-and-skills__pill .visually-hidden");
    let work_setting_type = "N/A";
    let employment_type = "N/A";

    hiddenElements.forEach((element) => {
        const textContent = element.textContent?.trim().toLowerCase();
        if (textContent.includes("workplace type is")) {
            if (textContent.includes("remote")) work_setting_type = "remote";
            else if (textContent.includes("hybrid")) work_setting_type = "hybrid";
            else if (textContent.includes("on-site") || textContent.includes("onsite")) work_setting_type = "onsite";
        } else if (textContent.includes("job type is")) {
            if (textContent.includes("full-time")) employment_type = "fulltime";
            else if (textContent.includes("part-time")) employment_type = "parttime";
            else if (textContent.includes("contract")) employment_type = "contract";
        }
    });

    const location = extractText(".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis");
    const country = location.includes(",") ? location.split(",").pop().trim() : location;
    const city = location.includes(",") ? location.split(",")[0].trim() : "N/A";

    return { work_setting_type, employment_type, country, city };
}

// Handle message from background script
chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "extract_job_details") {
        console.log("Extracting job details.");
        const jobData = {
            title: extractText(".job-details-jobs-unified-top-card__job-title h1"),
            company: extractText(".job-details-jobs-unified-top-card__company-name a"),
            location: extractText(".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis"),
            description: extractText(".jobs-description__content .jobs-box__html-content"),
            url: window.location.href,
            ...extractAdditionalDetails()
        };

        chrome.runtime.sendMessage({ action: "save_yaml", data: jobData }, (response) => {
            console.log("Job data sent to background script:", jobData);
        });
    }
});
