import * as jsyaml from './js-yaml.mjs';

// Country to ISO mapping function
const countryToISO = (countryName) => {
    const isoMapping = {
        "Germany": "DE",
        "United States": "US",
        "Canada": "CA",
        "United Kingdom": "GB",
        "France": "FR",
        "Remote": "N/A", // You can handle remote cases explicitly
        // Add other countries as needed
    };
    return isoMapping[countryName] || "N/A";
};

chrome.commands.onCommand.addListener((command) => {
    if (command === "extract-job-details") {
        console.log("Keyboard shortcut triggered: Extracting job details.");

        // Send a message to the content script to extract job details
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs.length > 0) {
                chrome.tabs.sendMessage(tabs[0].id, { action: "extract_job_details" });
            }
        });
    }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'save_yaml') {
        try {
            // Extract and convert the country to ISO code
            const countryName = message.data.country || "Remote";
            const isoCode = countryToISO(countryName);

            // Prepare the data in the required YAML template structure
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
                description: `|\n  ${message.data.description || "No description provided."}`,
            };

            // Convert the job data to YAML format
            const yamlData = jsyaml.dump(yamlTemplate);

            // Use a `data:` URL for the download
            const dataUrl = `data:text/yaml;charset=utf-8,${encodeURIComponent(yamlData)}`;

            // Helper function to sanitize filename parts
            function sanitizeFilenamePart(part) {
                return part.replace(/[^a-zA-Z0-9_\-]/g, "").replace(/ /g, "_").trim();
            }

            // Trigger a download of the YAML file
            chrome.downloads.download({
                url: dataUrl,
                filename: `${sanitizeFilenamePart(yamlTemplate.company)}_${sanitizeFilenamePart(yamlTemplate.title)}_job_details.yaml`,
            });

            console.log('YAML file created and download triggered.');
        } catch (error) {
            console.error('Error while converting data to YAML:', error);
        }
    }
});
