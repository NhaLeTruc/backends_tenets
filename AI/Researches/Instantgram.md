# Codebase Review Summary

Here's what I found in the Instantgram codebase:

🎯 What It Is
Instantgram is a clever bookmarklet tool (v5.1.1) that allows users to download images and videos from Instagram directly in their browser - no extension or app installation required. Users simply drag a button to their bookmark bar and click it while viewing Instagram content.

🏗️ Architecture
Current Branch Status: This appears to be the gh-pages deployment branch containing only the compiled website. The actual source code has been removed (noted in the CHANGELOG: "Remove code from repo").

Bookmarklet Structure (~14KB minified JavaScript):

4 Core Modules that run in cascade:
ImageVideoInStories - Handles Instagram Stories
VideoInPostAndModal - Handles videos in posts
ImageInPostAndModal - Handles images in posts
ImageOnScreen - Fallback image detector
Website: Built with Astro v4.14.3, using the Cayman GitHub Pages theme

🔧 Technical Highlights
Clever Implementation:

No external dependencies - completely self-contained
Exploits React internals - accesses Instagram's React Fiber tree to extract media URLs that aren't visible in the DOM
Smart video quality selection - parses MPEG-DASH manifests to prefer HD quality
Intelligent filtering - excludes profile pictures and UI elements from downloads
Key Technologies:

Vanilla JavaScript (ES6+)
React Fiber introspection
DOM manipulation and traversal
MPEG-DASH manifest parsing
✅ Supported Features
Media Types:

Single images/videos in posts
Carousel posts (multiple images/videos)
Instagram Stories
Reels
IGTV
Canvas images
Languages: English, German, Spanish, Portuguese (auto-detected)

Browser Support: Chrome ✅, Edge (Chromium) ✅, IE11 ✅, Firefox ⚠️ (limited), Edge Legacy ⚠️ (limited)

📁 Project Structure
├── index.html              # Main landing page
├── _astro/                 # Compiled Astro assets
├── lang/                   # Localized versions (de-de, en-us, es-es, pt-br)
├── stylesheets/            # CSS files
├── assets/img/             # Demo images
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md

🔍 Notable Patterns
The code uses a cascading detection strategy where each module tries to detect and extract media, returning success/failure. If one module fails, the next one tries. This makes it robust across different Instagram page types (feed, stories, modals, etc.).

⚠️ Important Note
Based on the CHANGELOG (v5.1.0), this project underwent a monorepo transformation using Turbo and pnpm. The source code you're seeing here is the compiled output for GitHub Pages deployment, not the actual development source.

## how to develop a similar bookmarklet tool for downloading media from web platforms. This is a great educational question about browser-based tools.

High-Level Architecture
1. Bookmarklet Fundamentals
A bookmarklet is JavaScript code that runs in the context of the current page. The basic structure:

javascript:(function(){ /* your code here */ })();
Key constraints:

Must be a single line of code
Runs in the page's context (has access to the DOM and page variables)
Subject to same-origin policy
Limited by URL length (typically 2000-2048 characters)
Can inject additional scripts if needed
2. Development Approach
Two-phase strategy:

Development: Write modular, readable code
Production: Minify into a single bookmarklet URL
Recommended workflow:

Develop as normal JavaScript modules
Use a build tool (webpack, rollup, esbuild) to bundle
Minify with terser or uglify-js
Wrap in bookmarklet format
Test in actual browser bookmark bar
Core Technical Challenges
Challenge 1: Finding Media URLs
Modern web apps (like Instagram) don't always put media URLs directly in the DOM. You need multiple strategies:

Strategy A: DOM Scraping

Find <img> and <video> elements
Extract src, srcset, or data-* attributes
Handle lazy-loaded content
Filter out UI elements (icons, avatars, thumbnails)
Strategy B: Framework Internals

React: Access component instances via __reactInternalInstance$ or similar
Vue: Access __vue__ property
Angular: Access component data through zone context
Navigate the virtual DOM tree to find props/state containing URLs
Strategy C: Network Interception

Listen to fetch or XMLHttpRequest
Intercept network responses
Parse JSON payloads for media URLs
More reliable but requires injecting before page load
Strategy D: API Reverse Engineering

Inspect network tab to find API endpoints
Replicate API calls with proper headers
Parse JSON responses
Requires maintaining endpoint knowledge
Challenge 2: State Management
Web apps have complex state:

Modal/Overlay Detection:

Check for overlay elements with high z-index
Look for ARIA attributes (role="dialog")
Handle focus traps and keyboard navigation
Carousel/Slider Detection:

Find active slide indicators
Navigate state through React/Vue components
Look for .active, aria-current, or transform values
Dynamic Content:

Use MutationObserver to watch DOM changes
Wait for content to load before extraction
Handle infinite scroll scenarios
Challenge 3: Browser Compatibility
Different rendering engines:

Chrome/Edge (Blink): Most features available
Firefox (Gecko): Can't drag bookmarklets, different selectors
Safari (WebKit): Strict security policies
Mobile browsers: Limited bookmark support
Strategies:

Feature detection over browser detection
Polyfills for older browsers (Promise, fetch, etc.)
Graceful degradation
CSS selector variations by browser
Challenge 4: Video Quality Selection
Video streaming uses adaptive formats:

HLS (HTTP Live Streaming):

Parse .m3u8 manifest files
Extract variant playlists with different qualities
Select highest bandwidth stream
MPEG-DASH:

Parse XML manifest
Find representations with quality labels
Prefer "hd", "high", or highest bandwidth
Implementation approach:

Fetch manifest URL
Parse with DOMParser (for XML) or text parsing (for M3U8)
Build quality selection logic
Return direct video URL
Development Architecture
Modular Design Pattern
1. Module System

Core Orchestrator
├── Detection Modules (run in cascade)
│   ├── StoriesModule
│   ├── VideoModule
│   ├── ImageModule
│   └── FallbackModule
├── Helper Functions
│   ├── getReactInstance()
│   ├── parseManifest()
│   ├── isInViewport()
│   └── filterProfileImages()
├── UI Module
│   ├── showNotification()
│   ├── showError()
│   └── createDownloadButton()
└── Localization Module
    └── getTranslation()
2. Cascade Pattern Each module returns boolean (success/failure):

Try Stories module → Success? Done. Failed? Continue.
Try Video module → Success? Done. Failed? Continue.
Try Image module → Success? Done. Failed? Continue.
Try Fallback → Last resort
3. Separation of Concerns

Detection: Find media on page
Extraction: Get URLs from elements/state
Processing: Handle quality, CDN, URL manipulation
Action: Download or open in new tab
UI/UX Considerations
Feedback to user:

Success notification: "Found 3 images!"
Error handling: "No media found on this page"
Loading states: "Searching for media..."
Progress indicators for multiple downloads
Download methods:

Open in new tab (Instantgram's approach)

Simple, always works
User must right-click → Save As
Trigger direct download

Create <a> element with download attribute
Programmatically click it
Blocked by CORS for cross-origin resources
Copy to clipboard

Copy media URL
User pastes into address bar
Internationalization Strategy
1. Embedded translations:

const messages = {
  'en-US': { success: 'Found media!' },
  'es-ES': { success: '¡Medios encontrados!' },
  'de-DE': { success: 'Medien gefunden!' }
};
2. Language detection:

navigator.language or navigator.languages[0]
Fallback to English
Allow user override via localStorage
3. Compact storage:

Only include strings used in UI
Use short keys to reduce size
Consider using language codes as keys
Build Pipeline
Development → Production Flow:

Source Code (src/)

Write in modern ES6+ modules
Use descriptive variable names
Add comments and documentation
Bundling (webpack/rollup)

Combine modules into single file
Tree-shake unused code
Resolve imports
Transpilation (Babel)

Convert ES6+ to ES5 for older browsers
Polyfill missing features
Handle async/await
Minification (terser)

Remove whitespace and comments
Mangle variable names
Optimize code structure
Bookmarklet Wrapping

Wrap in javascript:(function(){...})();
URL-encode special characters
Test length constraints
Deployment

Generate landing page with drag-and-drop button
Include installation instructions
Provide manual copy/paste fallback
Testing Strategy
1. Manual Testing:

Test on actual target website
Try different page types (feed, stories, profiles)
Test in different browsers
Verify on mobile browsers
2. Edge Cases:

Empty pages (no media)
Single vs. multiple media
Different media types simultaneously
Rapid navigation (SPA routing)
Slow network (loading states)
3. Update Monitoring:

Target websites change frequently
Monitor for breakage
Set up alerts for failures
Version the bookmarklet
Security & Ethics Considerations
Security:

Never collect user data
Don't make external network calls (privacy)
Avoid executing arbitrary code
Sanitize any user input
Ethics:

Respect copyright and terms of service
Don't enable bulk scraping
Add rate limiting
Include disclaimer about responsible use
Privacy:

No analytics in the bookmarklet itself
No tracking or telemetry
Open source for transparency
Maintenance Challenges
Website Changes:

DOM structure changes → Update selectors
Framework updates → Update internal access methods
API changes → Update network interception
New features → Add support for new media types
Version Management:

Include version number in code
Check for updates on run
Notify users of new versions
Maintain backward compatibility
Community Support:

GitHub issues for bug reports
Wiki for troubleshooting
Contribution guidelines
Changelog for transparency
Alternative Approaches
Browser Extension:

More power (background scripts, permissions)
Can intercept network before page load
Better UX with toolbar buttons
Requires installation and store approval
Userscript (Greasemonkey/Tampermonkey):

Runs automatically on page load
Can modify page before rendering
Easier to update
Requires script manager extension
Proxy/Server-side:

Bypass CORS restrictions
Server-side rendering/parsing
API caching
Requires hosting and maintenance
Modern Best Practices
Use ES6+ features (transpile for old browsers)
Implement error boundaries (try/catch around modules)
Add timeout mechanisms (don't hang forever)
Optimize bundle size (every byte counts in URLs)
Use semantic selectors (data attributes over classes)
Implement retry logic (for network requests)
Cache expensive operations (manifest parsing)
Use requestAnimationFrame (for DOM measurements)
The key insight from Instantgram is the cascade pattern with multiple detection strategies. Modern web apps are complex, so you need fallback upon fallback. The React internals approach is particularly clever - it's more stable than DOM selectors since component props change less frequently than HTML structure.

Would you like me to dive deeper into any specific aspect, such as React Fiber navigation, manifest parsing techniques, or build pipeline setup?
