import * as jsyaml from './js-yaml.mjs';

// Country to ISO mapping function
const countryToISO = (countryName) => {
    const isoMapping = {
        "Germany": "DE",
        "United States": "US",
        "Canada": "CA",
        "United Kingdom": "GB",
        "France": "FR",
        "Remote": "N/A"
    };
    return isoMapping[countryName] || "N/A";
};

// Handle keyboard shortcut
chrome.commands.onCommand.addListener((command) => {
    if (command === "extract-job-details") {
        console.log("Keyboard shortcut triggered: Extracting job details.");
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs.length > 0) {
                chrome.tabs.sendMessage(tabs[0].id, { action: "extract_job_details" });
            }
        });
    }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'save_yaml') {
        try {
            const countryName = message.data.country || "Remote";
            const isoCode = countryToISO(countryName);

            const yamlTemplate = {
                title: message.data.title || "N/A",
                company: message.data.company || "N/A",
                user_id: "be2ffb22-4b5b-4875-8b9a-06eb02d24421",
                status: "added",
                country: isoCode,
                city: message.data.city || "Remote",
                work_setting_type: message.data.work_setting_type || "remote",
                employment_type: message.data.employment_type || "fulltime",
                platform: "LinkedIn",
                url: message.data.url || "N/A",
                notes: "",
                description: `|\n  ${message.data.description || "No description provided."}`
            };

            const yamlData = jsyaml.dump(yamlTemplate);
            const dataUrl = `data:text/yaml;charset=utf-8,${encodeURIComponent(yamlData)}`;

            const sanitizeFilenamePart = (part) => part.replace(/[^a-zA-Z0-9_\-]/g, "").replace(/ /g, "_").trim();
            const filename = `${sanitizeFilenamePart(yamlTemplate.company)}_${sanitizeFilenamePart(yamlTemplate.title)}_job_details.yaml`;

            chrome.downloads.download({ url: dataUrl, filename });
            console.log("YAML file created and download triggered.");
        } catch (error) {
            console.error("Error while converting data to YAML:", error);
        }
    }
});
