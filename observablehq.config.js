// See https://observablehq.com/framework/config for documentation.

// Set up config to work with GitHub Pages
const isGitHubPages = process.env.DEPLOY_TARGET === "gh-pages";

export default {

 // If deploying to GitHub Pages, add subdirectory to path.
  base: isGitHubPages ? "/visualizing_intertextuality/" : "/",

  // The app’s title; used in the sidebar and webpage titles.
  title: "Visualizing Intertextuality",

  // The pages and sections in the sidebar. If you don’t specify this option,
  // all pages will be listed in alphabetical order. Listing pages explicitly
  // lets you organize them into sections and have unlisted pages.
  pages: [
    {
      name: "", // this puts a bold header at the head of the section
      pages: [
        {name: "Main Page", path: "/"},
        {name: "About the Project", path: "/about"},
        {name: "Full Intertext Diagram", path: "/sankey"},
        {name: "Thanks and Acknowledgements", path: "/thanks"},
        {name: "Frequently Asked Questions", path: "/faq"},
      ]
    },
  ],

  // Content to add to the head of the page, e.g. for a favicon:
  head: '<link rel="icon" href="observable.png" type="image/png" sizes="32x32">',

  // The path to the source root.
  root: "src",

  // Some additional configuration options and their defaults:
  // theme: "default", // try "light", "dark", "slate", etc.
  // header: "", // what to show in the header (HTML)
  // footer: "Built with Observable.", // what to show in the footer (HTML)
  // sidebar: true, // whether to show the sidebar
  // toc: true, // whether to show the table of contents
  // pager: true, // whether to show previous & next links in the footer
  output: "dist", // path to the output root for build
  // search: true, // activate search
  // linkify: true, // convert URLs in Markdown to links
  // typographer: false, // smart quotes and other typographic improvements
  // preserveExtension: false, // drop .html from URLs
  // preserveIndex: false, // drop /index from URLs
  
  // MODIFY LIST OF INTERPRETERS:
  interpreters: {
	".py": ["python"]
  },
  
};
