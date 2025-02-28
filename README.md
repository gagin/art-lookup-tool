# Vancouver Public Art Status Tools for Open WebUI

This tool provides functions for looking up the activity status of
Vancouver public art objects when using a RAG setup with Open WebUI.

## Problem Solved

When working with a RAG system containing documents about Vancouver
public art objects, some of the art may no longer be in place or may
have been decommissioned. These tools allow your LLM to:

1.  Check if a specific artwork is still in place or not.
2.  Focus responses on active artworks while still providing historical
    information.
3.  Compare multiple artworks to see which ones can still be visited.
4.  Avoid including status information for all artworks in every request
    context.
5.  List artworks by neighborhood.
6.  List known neighbourhoods.

## Prerequisites

-   Python 3.7+
-   requests library (install with `pip install requests`)

## Setup Instructions for Open WebUI

1.  Install the Tool

    1.  Go to Open WebUI admin panel
    2.  Navigate to \"Tools\" section
    3.  Click on \"Upload New Tool\"
    4.  Upload the `vancouver_art_status_tools.py` file
    5.  When configuring the tool:
        -   **Name**: Use \"VancouverArtStatus\" (important: this name
            will be part of the function names the model sees)
        -   **Description**: Use \"Tools for checking the status of
            Vancouver public art installations - whether they are
            currently on display or have been removed\"
        -   **Tags**: Optionally add tags like \"vancouver\", \"art\",
            \"public art\"
    6.  Save the tool

    The file already follows the required Open WebUI format with a
    `Tools` class containing the tool functions.

    **Important Note about Tool Naming**: The name you give to the tool
    in Open WebUI\'s configuration is important, as it forms part of the
    function names that the model will see and use. The model treats
    these names as informational, so choose a clear, descriptive name
    that indicates the tool\'s purpose.

2.  Configure Your Model

    1.  Create or edit a model in Open WebUI
    2.  Enable function calling for the model
    3.  Add the Vancouver Art Status tools to your model
    4.  Update your system prompt to inform the model about these tools,
        making sure the function names match what you configured in the
        previous step. Example system prompt:

    ``` none
    You have access to the VancouverArtStatus tool, which provides information about Vancouver public art objects.

    The tool has the following methods:

    * **get_artwork_status(artwork_name: str, include_details: bool = False):**
        * Use this method when a user asks about the status of a specific artwork.
        * ``artwork_name``: The name or title of the artwork.
        * ``include_details``: Optional boolean, if true, location, neighborhood, and a description excerpt will be included.
        * This method returns the current status of the artwork (e.g., "In place", "No longer in place").
    * **list_active_artworks(neighborhood: str = "", limit: int = 5):**
        * Use this method to suggest currently active artworks, optionally filtered by neighborhood.
        * ``neighborhood``: Optional neighborhood to filter by (e.g., "Stanley Park", "Downtown").
        * ``limit``: Optional maximum number of results to return (default 5).
        * This method returns a list of active artworks with their titles and locations.
    * **compare_artwork_status(artwork_names: str):**
        * Use this method when comparing the status of multiple artworks.
        * ``artwork_names``: A comma-separated list of artwork names or titles.
        * This method returns a comparison of the artworks' status, indicating which are currently in place.
    * **list_artworks_by_neighborhood(neighborhood: str, limit: int = 10):**
        * Use this method to list all artworks located within a specific neighborhood.
        * ``neighborhood``: The neighborhood to filter by (e.g., "Stanley Park", "Downtown").
        * ``limit``: Maximum number of results to return (default 10).
        * This method returns a list of artworks in the specified neighborhood with their titles and statuses.
    * **list_known_neighborhoods():**
        * Use this method to list all known neighborhoods where public artworks are located.
        * This method returns a list of known neighborhoods.

    When discussing artworks, prioritize ones that are still "In place," but be prepared to provide historical information about removed ones. For artworks that are "No longer in place" or "Deaccessioned," clearly inform the user that these cannot be visited currently.

    When a user asks about neighborhoods, or for a list of them, you must use the list_known_neighborhoods() tool.

    Example usage:
    User: "What neighborhoods have art?"
    You: tool_code
    print(VancouverArtStatus.list_known_neighborhoods())

    User: "Is the 'Giant' sculpture still there?"
    You: tool_code
    print(VancouverArtStatus.get_artwork_status(artwork_name='Giant'))
    ```

    Note: The function names in the system prompt include the tool name
    prefix (\"VancouverArtStatus.\"). This matches how Open WebUI
    exposes the functions to the model based on the tool name you
    configured.

## Available Tools

The examples below use the functions as they would appear to the model
if you named the tool \"VancouverArtStatus\" during setup.

1.  VancouverArtStatus.get_artwork_status

    Gets the current status of a Vancouver public art object (whether
    it\'s still in place or removed).

    **Parameters:**

    -   `artwork_name`: The name of the artwork to check status for
    -   `include_details`: Whether to include additional details about
        the artwork (default: false)

    **Example:**

    ``` none
    User: Is the Digital Orca still on display?

    AI: *uses VancouverArtStatus.get_artwork_status("Digital Orca")*

    Response: Artwork: Digital Orca
    Status: In place
    ```

2.  VancouverArtStatus.list_active_artworks

    Lists Vancouver public artworks that are currently in place,
    optionally filtered by neighborhood.

    **Parameters:**

    -   `neighborhood`: Optional neighborhood to filter by (e.g.,
        \"Stanley Park\", \"Downtown\")
    -   `limit`: Maximum number of results to return (default: 5)

    **Example:**

    ``` none
    User: What public art can I see in Stanley Park?

    AI: *uses VancouverArtStatus.list_active_artworks("Stanley Park")*

    Response: Found 12 active artworks in or near Stanley Park (showing 5):

    1. Entrance to the Underworld - Located at: S side of entrance to Lost Lagoon (Stanley Park)
    2. Girl in Wetsuit - Located at: In water, past Brockton Point, N side of Stanley Park (Stanley Park)
    3. Harry Jerome - Located at: Stanley Park Drive (Stanley Park)
    4. Lumbermans Arch - Located at: Stanley Park Drive (Stanley Park)
    5. Rhoda and Hosea - Located at: Stanley Park (Stanley Park)

    There are 7 more active artworks.
    ```

3.  VancouverArtStatus.compare_artwork_status

    Compares the status of multiple Vancouver public artworks to see
    which ones are currently in place.

    **Parameters:**

    -   `artwork_names`: Comma-separated list of artwork names or titles
        to compare

    **Example:**

    ``` none
    User: Are the Digital Orca, Girl in Wetsuit, and The Drop still on display?

    AI: *uses VancouverArtStatus.compare_artwork_status("Digital Orca, Girl in Wetsuit, The Drop")*

    Response: Artwork Status Comparison:

    Currently in place:
    1. Digital Orca
    2. Girl in Wetsuit
    3. The Drop
    ```

4.  VancouverArtStatus.list_artworks_by_neighborhood

    List all artworks located within a specific neighborhood.

    **Parameters:**

    -   `neighborhood`: The neighborhood to filter by (e.g., \"Stanley
        Park\", \"Downtown\").
    -   `limit`: Maximum number of results to return (default 10).

    **Example:**

    ``` none
    User: What artworks are in Stanley Park?

    AI: *uses VancouverArtStatus.list_artworks_by_neighborhood("Stanley Park")*

    Response: Found 12 artworks in Stanley Park (showing 10):
    1. Entrance to the Underworld - Status: In place
    2. Girl in Wetsuit - Status: In place
    3. Harry Jerome - Status: In place
    4. Lumbermans Arch - Status: In place
    5. Rhoda and Hosea - Status: In place
    6. The Drop - Status: In place
    7. A-maze-ing Laughter - Status: In place
    8. Inukshuk - Status: In place
    9. Japanese Canadian War Memorial - Status: In place
    ```

General issues with RAG+tools setup in Open-WebUI
\-\-\-\-\-\-\-\-\-\-\-\-\-\-- Seems like it vector-matches full
questions, and every question, even if it clearly asks to use tools - It
sometimes returns in the dialog the tool call text instead of calling
the actual tool - Even when citations are off, the answers still include
references like \[1\] to non-existing referred documents, and several
references to the same documents
