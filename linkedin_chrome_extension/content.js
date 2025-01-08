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
        const textContent = element.innerText.toLowerCase();
        if (textContent.includes("workplace type is")) {
            if (textContent.includes("remote")) {
                work_setting_type = "remote";
            } else if (textContent.includes("hybrid")) {
                work_setting_type = "hybrid";
            } else if (textContent.includes("on-site") || textContent.includes("onsite")) {
                work_setting_type = "on-site";
            }
        } else if (textContent.includes("job type is")) {
            if (textContent.includes("full-time")) {
                employment_type = "fulltime";
            } else if (textContent.includes("part-time")) {
                employment_type = "parttime";
            } else if (textContent.includes("contract")) {
                employment_type = "contract";
            }
        }
    });

    // Extract country and city from location
    const location = extractText(".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis");
    const country = location.includes(",") ? location.split(",").pop().trim() : location; // Part after the last comma
    const city = location.includes(",") ? location.split(",")[0].trim() : "N/A"; // Part before the first comma

    return { work_setting_type, employment_type, country, city };
}

// Extract job details
const jobData = {
    title: extractText(".job-details-jobs-unified-top-card__job-title h1"), // Job title
    company: extractText(".job-details-jobs-unified-top-card__company-name a"), // Company name
    location: extractText(".job-details-jobs-unified-top-card__primary-description-container span.tvm__text--low-emphasis"), // Location
    description: extractText(".jobs-description__content .jobs-box__html-content"), // Job description
    url: window.location.href, // Current page URL
    ...extractAdditionalDetails(), // Add work setting type, employment type, country, and city
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
