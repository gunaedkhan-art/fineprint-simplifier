#!/usr/bin/env python3
"""
Test script for sitemap generation
"""

import os
from sitemap_generator import SitemapGenerator

def test_sitemap():
    print("🧪 Testing Sitemap Generation")
    print("=" * 40)
    
    # Test with different base URLs
    test_urls = [
        "https://your-domain.com",
        "https://fineprint-simplifier.herokuapp.com",
        "https://fineprint-simplifier.railway.app"
    ]
    
    for base_url in test_urls:
        print(f"\n📍 Testing with base URL: {base_url}")
        
        generator = SitemapGenerator(base_url)
        
        # Test sitemap generation
        sitemap_xml = generator.generate_sitemap_xml()
        print(f"✅ Sitemap XML generated ({len(sitemap_xml)} characters)")
        
        # Test robots.txt generation
        robots_txt = generator.generate_robots_txt()
        print(f"✅ Robots.txt generated ({len(robots_txt)} characters)")
        
        # Show sample content
        print("\n📄 Sample Sitemap XML:")
        print("-" * 30)
        print(sitemap_xml[:500] + "..." if len(sitemap_xml) > 500 else sitemap_xml)
        
        print("\n📄 Sample Robots.txt:")
        print("-" * 30)
        print(robots_txt)
        
        print("\n" + "=" * 40)

def show_environment_setup():
    print("\n🔧 Environment Setup for Production:")
    print("=" * 40)
    print("Set the BASE_URL environment variable:")
    print("")
    print("Heroku:")
    print("  heroku config:set BASE_URL=https://your-domain.com")
    print("")
    print("Railway:")
    print("  BASE_URL=https://your-domain.com")
    print("")
    print("Local Development:")
    print("  set BASE_URL=http://localhost:8000")
    print("")
    print("📋 URLs to submit to Google Search Console:")
    print("  https://your-domain.com/sitemap.xml")
    print("  https://your-domain.com/robots.txt")

if __name__ == "__main__":
    test_sitemap()
    show_environment_setup()
