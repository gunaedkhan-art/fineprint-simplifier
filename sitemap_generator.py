# sitemap_generator.py - Dynamic sitemap generation

from fastapi import Request
from fastapi.responses import Response
from datetime import datetime
import os
from typing import List, Dict, Any

class SitemapGenerator:
    """Generate dynamic XML sitemaps for SEO"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("BASE_URL", "https://smallprintchecker.com")
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]
    
    def get_static_pages(self) -> List[Dict[str, Any]]:
        """Get list of static pages with their metadata"""
        return [
            {
                "url": "/",
                "changefreq": "weekly",
                "priority": "1.0",
                "lastmod": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "url": "/upload",
                "changefreq": "monthly",
                "priority": "0.9",
                "lastmod": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "url": "/compare",
                "changefreq": "monthly",
                "priority": "0.8",
                "lastmod": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "url": "/how-it-works",
                "changefreq": "monthly",
                "priority": "0.7",
                "lastmod": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "url": "/pricing",
                "changefreq": "weekly",
                "priority": "0.8",
                "lastmod": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "url": "/admin/login",
                "changefreq": "yearly",
                "priority": "0.1",
                "lastmod": datetime.now().strftime("%Y-%m-%d")
            }
        ]
    
    def get_dynamic_pages(self) -> List[Dict[str, Any]]:
        """Get list of dynamic pages (if any)"""
        # For now, we don't have dynamic pages, but this can be extended
        # to include user-generated content, blog posts, etc.
        return []
    
    def generate_sitemap_xml(self) -> str:
        """Generate XML sitemap content"""
        pages = self.get_static_pages() + self.get_dynamic_pages()
        
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for page in pages:
            xml_content += '  <url>\n'
            xml_content += f'    <loc>{self.base_url}{page["url"]}</loc>\n'
            xml_content += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
            xml_content += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
            xml_content += f'    <priority>{page["priority"]}</priority>\n'
            xml_content += '  </url>\n'
        
        xml_content += '</urlset>'
        
        return xml_content
    
    def generate_robots_txt(self) -> str:
        """Generate robots.txt content"""
        robots_content = f"User-agent: *\n"
        robots_content += f"Allow: /\n"
        robots_content += f"Disallow: /admin/\n"
        robots_content += f"Disallow: /api/\n"
        robots_content += f"Disallow: /static/\n"
        robots_content += f"\n"
        robots_content += f"Sitemap: {self.base_url}/sitemap.xml\n"
        
        return robots_content

# Global sitemap generator instance
sitemap_generator = SitemapGenerator()

def get_sitemap_xml() -> str:
    """Get the current sitemap XML"""
    return sitemap_generator.generate_sitemap_xml()

def get_robots_txt() -> str:
    """Get the current robots.txt"""
    return sitemap_generator.generate_robots_txt()

def update_base_url(base_url: str):
    """Update the base URL for sitemap generation"""
    global sitemap_generator
    sitemap_generator = SitemapGenerator(base_url)
