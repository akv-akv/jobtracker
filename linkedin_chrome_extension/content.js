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
    // Work setting type (e.g., Remote, Hybrid)
    const workSettingTypeElement = document.querySelector(".job-details-preferences-and-skills__pill .ui-label");
    const workSettingType = workSettingTypeElement
        ? workSettingTypeElement.innerText.toLowerCase().includes("remote")
            ? "remote"
            : workSettingTypeElement.innerText.toLowerCase().includes("hybrid")
            ? "hybrid"
            : "on-site"
        : "N/A";

    // Employment type (e.g., Full-time, Part-time)
    const employmentTypeElement = document.querySelector(".job-details-preferences-and-skills__pill .ui-label--accent-3");
    const employmentType = employmentTypeElement ? employmentTypeElement.innerText.trim() : "N/A";

    // Extract country from location
    const location = extractText(".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis");
    const country = location.includes(",") ? location.split(",").pop().trim() : location; // Use part after the last comma

    return { workSettingType, employmentType, country };
}

// Extract job details
const jobData = {
    title: extractText(".job-details-jobs-unified-top-card__job-title h1"), // Job title
    company: extractText(".job-details-jobs-unified-top-card__company-name a"), // Company name
    location: extractText(".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis"), // Location
    description: extractText(".jobs-description__content .jobs-box__html-content"), // Job description
    url: window.location.href, // Current page URL
    ...extractAdditionalDetails(), // Add work setting type, employment type, and country
};

// Validate extracted data
Object.keys(jobData).forEach((key) => {
    if (!jobData[key] || jobData[key] === "N/A") {
        console.warn(`Missing or incomplete data for field: ${key}`);
    }
});

// Send job data to the background script for processing
chrome.runtime.sendMessage({ action: "save_yaml", data: jobData }, (response) => {
    console.log("Job data sent to background script:", jobData);
});
