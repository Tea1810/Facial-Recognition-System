// camera.js - Camera management

let videoFeedActive = false;

/**
 * Start video feed for a specific element
 * @param {string} elementId - ID of the video element
 */
function startVideoFeed(elementId) {
    const videoElement = document.getElementById(elementId);
    if (videoElement) {
        // Add timestamp to prevent caching
        videoElement.src = `/video_feed?t=${new Date().getTime()}`;
        videoFeedActive = true;
    }
}

/**
 * Stop video feed for a specific element
 * @param {string} elementId - ID of the video element
 */
function stopVideoFeed(elementId) {
    const videoElement = document.getElementById(elementId);
    if (videoElement) {
        videoElement.src = '';
        videoFeedActive = false;
    }
    // Tell server to release camera
    fetch('/stop_camera').catch(err => console.log('Camera stop error:', err));
}

/**
 * Check if video feed is currently active
 * @returns {boolean} True if video is active
 */
function isVideoFeedActive() {
    return videoFeedActive;
}