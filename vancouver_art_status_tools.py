import os
import re
import glob
import json
from typing import Dict, List, Optional, Union, Any


class Tools:
    def __init__(self):
        self.status_db = {}
        self._load_status_database()
    
    def _load_status_database(self):
        """
        Load the status of all artwork from markdown files
        """
        # Path to the public art markdown files
        art_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public_art_vancouver")
        md_files = glob.glob(os.path.join(art_dir, "*.md"))
        
        for md_file in md_files:
            filename = os.path.basename(md_file)
            artwork_name = os.path.splitext(filename)[0]
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract title if available
                    title_match = re.search(r'## Title of Work\s*\n(.*?)\n', content, re.DOTALL)
                    title = title_match.group(1).strip() if title_match else artwork_name
                    
                    # Extract status
                    status_match = re.search(r'## Status\s*\n(.*?)\n', content, re.DOTALL)
                    status = status_match.group(1).strip() if status_match else "Unknown"
                    
                    # Extract additional info if we want it
                    description_match = re.search(r'## DescriptionOfwork\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                    description = description_match.group(1).strip() if description_match else ""
                    
                    location_match = re.search(r'## LocationOnsite\s*\n(.*?)\n', content, re.DOTALL)
                    location = location_match.group(1).strip() if location_match else ""
                    
                    neighborhood_match = re.search(r'## Neighbourhood\s*\n(.*?)\n', content, re.DOTALL)
                    neighborhood = neighborhood_match.group(1).strip() if neighborhood_match else ""
                    
                    # Store in database with lowercase keys for case-insensitive lookup
                    self.status_db[artwork_name.lower()] = {
                        "name": artwork_name,
                        "title": title,
                        "status": status,
                        "location": location,
                        "neighborhood": neighborhood,
                        "description": description[:300] + "..." if len(description) > 300 else description,
                        "filename": filename
                    }
                    
                    # Also index by title for easier lookup
                    if title.lower() != artwork_name.lower():
                        self.status_db[title.lower()] = {
                            "name": artwork_name,
                            "title": title,
                            "status": status,
                            "location": location,
                            "neighborhood": neighborhood,
                            "description": description[:300] + "..." if len(description) > 300 else description,
                            "filename": filename
                        }
            except Exception as e:
                print(f"Error processing {md_file}: {str(e)}")
        
        print(f"Loaded status for {len(self.status_db)} art objects")
    
    def get_artwork_status(self, artwork_name: str, include_details: bool = False) -> str:
        """
        Get the current status of a Vancouver public art object (whether it's still in place or removed)
        
        :param artwork_name: The name of the artwork to check status for. This can be the filename or the title of the work.
        :param include_details: Whether to include additional details about the artwork like location.
        :return: Information about the artwork's status and details if requested.
        """
        if not artwork_name:
            return "Error: No artwork name provided"
        
        # Try exact match (case insensitive)
        artwork_key = artwork_name.lower()
        if artwork_key in self.status_db:
            art = self.status_db[artwork_key]
            
            if include_details:
                details = []
                if art["location"]:
                    details.append(f"Location: {art['location']}")
                if art["neighborhood"]:
                    details.append(f"Neighborhood: {art['neighborhood']}")
                if art["description"]:
                    details.append(f"Description excerpt: {art['description']}")
                
                details_text = "\n".join(details) if details else "No additional details available"
                return f"Artwork: {art['title']}\nStatus: {art['status']}\n\n{details_text}"
            else:
                return f"Artwork: {art['title']}\nStatus: {art['status']}"
        
        # Try fuzzy match
        matches = []
        for key, data in self.status_db.items():
            if artwork_name.lower() in key or artwork_name.lower() in data["title"].lower():
                matches.append(data)
        
        if matches:
            response = f"Could not find exact match for '{artwork_name}', but found {len(matches)} similar artwork(s):\n\n"
            for i, match in enumerate(matches[:5], 1):  # Limit to top 5 matches
                response += f"{i}. {match['title']} - Status: {match['status']}\n"
            
            if len(matches) > 5:
                response += f"\nAnd {len(matches) - 5} more matches."
            
            return response
        
        return f"No artwork found matching '{artwork_name}'"
    
    def list_active_artworks(self, neighborhood: str = "", limit: int = 5) -> str:
        """
        List Vancouver public artworks that are currently in place, optionally filtered by neighborhood
        
        :param neighborhood: Optional neighborhood to filter by (e.g., "Stanley Park", "Downtown")
        :param limit: Maximum number of results to return (default 5)
        :return: List of active artworks with their titles and locations
        """
        active_artworks = []
        
        # Collect unique artworks (avoid duplicates from title/filename keys)
        seen_titles = set()
        
        for data in self.status_db.values():
            if data["title"] in seen_titles:
                continue
                
            if data["status"] == "In place":
                if not neighborhood or (data["neighborhood"] and neighborhood.lower() in data["neighborhood"].lower()):
                    active_artworks.append(data)
                    seen_titles.add(data["title"])
        
        # Sort by title
        active_artworks.sort(key=lambda x: x["title"])
        
        if not active_artworks:
            if neighborhood:
                return f"No active artworks found in the {neighborhood} neighborhood"
            else:
                return "No active artworks found"
        
        # Apply limit and format response
        limited_results = active_artworks[:limit]
        
        response = f"Found {len(active_artworks)} active artworks"
        if neighborhood:
            response += f" in or near {neighborhood}"
        response += f" (showing {len(limited_results)}):\n\n"
        
        for i, art in enumerate(limited_results, 1):
            response += f"{i}. {art['title']}"
            if art["location"]:
                response += f" - Located at: {art['location']}"
            if art["neighborhood"]:
                response += f" ({art['neighborhood']})"
            response += "\n"
        
        if len(active_artworks) > limit:
            response += f"\nThere are {len(active_artworks) - limit} more active artworks."
        
        return response
    
    def compare_artwork_status(self, artwork_names: str) -> str:
        """
        Compare the status of multiple Vancouver public artworks
        
        :param artwork_names: Comma-separated list of artwork names or titles to compare
        :return: Comparison of the artworks' status indicating which are currently in place
        """
        if not artwork_names:
            return "Error: No artwork names provided"
        
        names_list = [name.strip() for name in artwork_names.split(",") if name.strip()]
        
        if not names_list:
            return "Error: Invalid input format. Please provide a comma-separated list of artwork names."
        
        results = []
        
        for name in names_list:
            found = False
            name_key = name.lower()
            
            # Try exact match first
            if name_key in self.status_db:
                art = self.status_db[name_key]
                results.append({
                    "name": name,
                    "title": art["title"],
                    "status": art["status"],
                    "found": True
                })
                found = True
            else:
                # Try fuzzy match
                for key, data in self.status_db.items():
                    if name_key in key or name_key in data["title"].lower():
                        results.append({
                            "name": name,
                            "title": data["title"],
                            "status": data["status"],
                            "found": True
                        })
                        found = True
                        break
            
            if not found:
                results.append({
                    "name": name,
                    "found": False
                })
        
        # Format the response
        response = "Artwork Status Comparison:\n\n"
        
        in_place = []
        not_in_place = []
        not_found = []
        
        for result in results:
            if not result["found"]:
                not_found.append(result["name"])
            elif result["status"] == "In place":
                in_place.append(result["title"])
            else:
                not_in_place.append(f"{result['title']} ({result['status']})")
        
        if in_place:
            response += "Currently in place:\n"
            for i, title in enumerate(in_place, 1):
                response += f"{i}. {title}\n"
            response += "\n"
        
        if not_in_place:
            response += "Not currently in place:\n"
            for i, title in enumerate(not_in_place, 1):
                response += f"{i}. {title}\n"
            response += "\n"
        
        if not_found:
            response += "Not found in database:\n"
            for i, name in enumerate(not_found, 1):
                response += f"{i}. {name}\n"
        
        return response
    def list_active_artworks(self, neighborhood: str = "", limit: int = 5) -> str:
        """
        List Vancouver public artworks that are currently in place, optionally filtered by neighborhood.

        :param neighborhood: Optional neighborhood to filter by (e.g., "Stanley Park", "Downtown").
        :param limit: Maximum number of results to return (default 5).
        :return: List of active artworks with their titles and locations.
        """
        active_artworks = []
        seen_titles = set()

        for data in self.status_db.values():
            if data["title"] in seen_titles:
                continue

            if data["status"] == "In place":
                if not neighborhood or (data["neighborhood"] and neighborhood.lower() in data["neighborhood"].lower()):
                    active_artworks.append(data)
                    seen_titles.add(data["title"])

        active_artworks.sort(key=lambda x: x["title"])

        if not active_artworks:
            if neighborhood:
                return f"No active artworks found in the {neighborhood} neighborhood"
            else:
                return "No active artworks found"

        limited_results = active_artworks[:limit]

        response = f"Found {len(active_artworks)} active artworks"
        if neighborhood:
            response += f" in or near {neighborhood}"
        response += f" (showing {len(limited_results)}):\n\n"

        for i, art in enumerate(limited_results, 1):
            response += f"{i}. {art['title']}"
            if art["location"]:
                response += f" - Located at: {art['location']}"
            if art["neighborhood"]:
                response += f" ({art['neighborhood']})"
            response += "\n"

        if len(active_artworks) > limit:
            response += f"\nThere are {len(active_artworks) - limit} more active artworks."

        return response

    def compare_artwork_status(self, artwork_names: str) -> str:
        """
        Compare the status of multiple Vancouver public artworks.

        :param artwork_names: Comma-separated list of artwork names or titles to compare.
        :return: Comparison of the artworks' status indicating which are currently in place.
        """
        if not artwork_names:
            return "Error: No artwork names provided"

        names_list = [name.strip() for name in artwork_names.split(",") if name.strip()]

        if not names_list:
            return "Error: Invalid input format. Please provide a comma-separated list of artwork names."

        results = []

        for name in names_list:
            found = False
            name_key = name.lower()

            if name_key in self.status_db:
                art = self.status_db[name_key]
                results.append({
                    "name": name,
                    "title": art["title"],
                    "status": art["status"],
                    "found": True
                })
                found = True
            else:
                for key, data in self.status_db.items():
                    if name_key in key or name_key in data["title"].lower():
                        results.append({
                            "name": name,
                            "title": data["title"],
                            "status": data["status"],
                            "found": True
                        })
                        found = True
                        break

            if not found:
                results.append({
                    "name": name,
                    "found": False
                })

        response = "Artwork Status Comparison:\n\n"

        in_place = []
        not_in_place = []
        not_found = []

        for result in results:
            if not result["found"]:
                not_found.append(result["name"])
            elif result["status"] == "In place":
                in_place.append(result["title"])
            else:
                not_in_place.append(f"{result['title']} ({result['status']})")

        if in_place:
            response += "Currently in place:\n"
            for i, title in enumerate(in_place, 1):
                response += f"{i}. {title}\n"
            response += "\n"

        if not_in_place:
            response += "Not currently in place:\n"
            for i, title in enumerate(not_in_place, 1):
                response += f"{i}. {title}\n"
            response += "\n"

        if not_found:
            response += "Not found in database:\n"
            for i, name in enumerate(not_found, 1):
                response += f"{i}. {name}\n"

        return response
    
    def list_artworks_by_neighborhood(self, neighborhood: str, limit: int = 10) -> str:
        """
        List all Vancouver public artworks in a specific neighborhood.

        :param neighborhood: The neighborhood to filter by (e.g., "Stanley Park", "Downtown").
        :param limit: Maximum number of results to return (default 10).
        :return: List of artworks in the specified neighborhood with their titles and statuses.
        """
        artworks_in_neighborhood = []
        seen_titles = set()

        for data in self.status_db.values():
            if data["title"] in seen_titles:
                continue

            if data["neighborhood"] and neighborhood.lower() in data["neighborhood"].lower():
                artworks_in_neighborhood.append(data)
                seen_titles.add(data["title"])

        artworks_in_neighborhood.sort(key=lambda x: x["title"])

        if not artworks_in_neighborhood:
            return f"No artworks found in the {neighborhood} neighborhood."

        limited_results = artworks_in_neighborhood[:limit]

        response = f"Found {len(artworks_in_neighborhood)} artworks in {neighborhood} (showing {len(limited_results)}):\n\n"

        for i, art in enumerate(limited_results, 1):
            response += f"{i}. {art['title']} - Status: {art['status']}\n"

        if len(artworks_in_neighborhood) > limit:
            response += f"\nThere are {len(artworks_in_neighborhood) - limit} more artworks in this neighborhood."

        return response
    def list_known_neighborhoods(self) -> str:
        """
        Lists all known neighborhoods where public artworks are located.

        :return: A list of known neighborhoods.
        """
        neighborhoods = set()
        for data in self.status_db.values():
            if data["neighborhood"]:
                neighborhoods.add(data["neighborhood"])

        neighborhood_list = sorted(list(neighborhoods))

        if not neighborhood_list:
            return "No known neighborhoods found."

        return "Known neighborhoods:\n\n" + "\n".join(f"- {neighborhood}" for neighborhood in neighborhood_list)