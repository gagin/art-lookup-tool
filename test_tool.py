#!/usr/bin/env python3
"""
Test script for the Vancouver Art Status tools
"""

from vancouver_art_status_tools import Tools

def main():
    # Initialize tools
    print("Initializing tools and loading data...")
    tools = Tools()
    
    # Test get_artwork_status
    print("\n--- Testing get_artwork_status ---")
    artworks = ["Digital Orca", "Girl in Wetsuit", "The Drop"]
    for artwork in artworks:
        print(f"\nLooking up: {artwork}")
        print(tools.get_artwork_status(artwork, include_details=True))
    
    # Test with non-existent artwork
    print("\nLooking up non-existent artwork: Fake Artwork")
    print(tools.get_artwork_status("Fake Artwork"))
    
    # Test list_active_artworks
    print("\n--- Testing list_active_artworks ---")
    areas = ["Stanley Park", "Downtown"]
    for area in areas:
        print(f"\nListing artworks in: {area}")
        print(tools.list_active_artworks(neighborhood=area, limit=3))
    
    # Test compare_artwork_status
    print("\n--- Testing compare_artwork_status ---")
    comparison = "Digital Orca, Girl in Wetsuit, A Bright Future, NonExistent Artwork"
    print(f"\nComparing artworks: {comparison}")
    print(tools.compare_artwork_status(comparison))

if __name__ == "__main__":
    main()