document.addEventListener("DOMContentLoaded", () => {
  const extractJobButton = document.getElementById("extract-job");

  if (extractJobButton) {
      extractJobButton.addEventListener("click", () => {
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
              if (tabs.length > 0) {
                  // Inject content script if not already present
                  chrome.scripting.executeScript({
                      target: { tabId: tabs[0].id },
                      files: ["content.js"]
                  }, () => {
                      // Send a message to the content script
                      chrome.tabs.sendMessage(tabs[0].id, { action: "extract_job_details" });
                  });
              } else {
                  console.error("No active tab found.");
              }
          });
      });
  } else {
      console.error("Button with ID 'extract-job' not found.");
  }
});
