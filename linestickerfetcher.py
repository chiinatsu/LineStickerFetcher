import requests
import os
import sys
import json
import re
from bs4 import BeautifulSoup

def sanitize_filename(name):
    """
    Removes characters that are invalid for directory or file names.
    """
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Reduce multiple underscores to a single one
    sanitized = re.sub(r'__+', '_', sanitized)
    return sanitized.strip('_')

def download_from_url(url):
    """
    Fetches the HTML from a LINE STORE URL, parses it, and downloads the stickers.

    Args:
        url (str): The URL of the sticker pack on store.line.me.
    """
    print(f"Fetching data from URL: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch URL. Please check the link and your connection. Details: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('p', class_='mdCMN38Item01Ttl')
    if not title_tag:
        print("Error: Could not find the sticker pack title. The page layout may have changed.")
        return
        
    pack_title = sanitize_filename(title_tag.text.strip())
    
    if not os.path.exists(pack_title):
        os.makedirs(pack_title)
        print(f"Created directory: '{pack_title}'")

    sticker_items = soup.find_all('li', class_='FnStickerPreviewItem')

    if not sticker_items:
        print("Error: Could not find any stickers on this page. Make sure the URL is correct.")
        return

    print(f"\nFound {len(sticker_items)} stickers. Starting download...")

    for item in sticker_items:
        data_preview_str = item.get('data-preview')
        if not data_preview_str:
            continue

        try:
            preview_data = json.loads(data_preview_str)
            
            
            sticker_id = preview_data.get('id')
            if not sticker_id:
                print("\nWarning: Skipping an item without a sticker ID.")
                continue

            # Prioritize animated URL, fall back to static
            image_url = preview_data.get('animationUrl')
            is_animated = True
            
            if not image_url or image_url.strip() == "":
                image_url = preview_data.get('staticUrl')
                is_animated = False

            if not image_url or image_url.strip() == "":
                print(f"\nWarning: Could not find a valid URL for sticker ID {sticker_id}.")
                continue
            
            # Construct a unique filename using the ID
            if is_animated:
                file_name = f"{sticker_id}_animation.png"
            else:
                file_name = f"{sticker_id}.png"
            
            file_path = os.path.join(pack_title, file_name)

            img_response = requests.get(image_url, stream=True)
            if img_response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(img_response.content)
                
                sys.stdout.write(f"\rSuccessfully downloaded: {file_name}{' ' * 10}")
                sys.stdout.flush()
            else:
                sys.stdout.write(f"\rFailed to download {file_name}. Status: {img_response.status_code}\n")

        except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
            sys.stdout.write(f"\rAn error occurred while processing a sticker: {e}\n")
    
    print("\n\nDownload complete!")


if __name__ == "__main__":
    # Define the ASCII art as a multi-line string
    ascii_art = r"""
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@%.+====@@@@@@@@=====%@@@::.:.:.@@%@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@:::========@@@@-====@:..::.::::#-=*+#.::@::=====@@@@@@@@@@@@@
@@@=-::==========@+-#+::.:*+:.#-==--*-=*::+%=::-=====@@@@@*=-----
@@@==::@@@@@@@@@@@%..:@.:..:...@==%::..:.:-===:::@-::+@@=-===---=
@@@==%::@@@@@@@@#::.%..:.:::::::::@@#.+@::-===%:.:.:-::+=-=@@@@::
:@@==:::*@@@@@@#..-....*::::::::..=::+.=::-===@::::.+::=@@@@@@@:-
.@@@=::::%@@@@*.:-:...:..:......::.=:*.+:@#-===:.:::@:%@@@@@@@*-:
:..@@::::::*@+..=....:+::.....:..:.:@:.:#:.:@%=@.:..@%@@@@@@@@-::
...@@@@:::::*:.:*.::##=.:.:..:::::.:#===#=#==@#=#.-:..@@@@@@@=--:
...@@@@@@:::+::=:::-:.:.:.:::.:.::.::*==*-===@:.=@:%:.@@@@@@+:--+
..%@@@@@@@@@:..#.--....-.@#::::::.+:..+*:=:-%-:::@-:::-%@@@---+@@
@+@@@@@@@@@@:::##.@@@@@+::@::.:::%@@@%%%@@:::.::.@:%-::::%---@@@@
@@+@@@@@@@@@::.#@%-@--:-@+:+..:-@:@-:-:::=%:::::.@.::%:::::#@@@@@
@@@#@@@@@@@@.::%#...:++-..........*-=++=--%.:::::@:::-:+#::::#@@@
@@@@@@@@@=-#...##.@--++-.........%=--++::=%::::::@:@---%@@@::::@@
@@@@@@--:::-+:.@*.@----............@--::#=%:::::.:.%-%@@@@@@@::+*
@@@@*@@-:-:-*::#:-+#*+:..........:::-:-::-+:::::@..@@@@@@@@@@@#:*
@@@@@-@@@@@@@+:#:.........@==%...........=::.::::.%@@@@@@@@@@@@@@
@@@-+:@@:::@@@::=:........:===...........%:::::@@@=-=@@@@@@@@@@@@
@@@--@@@..#...=::=@........@=*..........*:::::@@@@@--=@@@@@@@@@%=
@@@-=-%@@:=:::++::---@:..............*@@#::::@@@@@@@====@@@@@@::-
@@@@-=--%@@=::*.:=::#....:+===@--#-::#@@:::%@@@@@@@@@=----=%===::
@@@@@+-=-=@@@-*::..:%%#....@.@.:..#=::+::+@@@@@@@@@@@@@---#====-:
@@@@@@@%-=--=#=#::-:::::::--:@@.@.:#+:+*::@@@@@@@@@@@@@@@======*=
@@@@@@@@@@@#=====#@######@:..=@...:#:--::...=@@@@@@@@@@#====*%%*-
@@@@@@@@@@====*=-=-=@@@@@@..:@:: .:#.+--:::....%@@@@@@%==+@@@@@@@
@@@@@@@@-:-#@@@@@====@@@-::%.@@:--%=:+:*-:::..:..-:@@@+@@@@@@@@@@
@@@@@@@+=+@@@@@@@@@--=@@@*:.@:@::++=-::=@+-:-.-*-:.*..%@@@@@@@@@@
@@@@@@@=-%@@@@@@@@@@===@@@@.:::::-::---:+@@----@::@::@::@@@@@@@@@
@@@@@@@%::@@@@@@@@@@%-=@@@@@---:-::*%%*#=+@@@@@@@@@@@%:::-@@@@@@@
@@@@@@@::::%@@@@@@*:@=@@@@@@+*#:--:#:::+:-=@@@@@@@@@@@-::::+@@@@+
@@@@@@@%:::::@@@-:--=@@@@-::-:-:::-+::--+:--@@@@@@@@@@@@-:::::*@-              
                                                                                                    
                                                                                                    
    """
    # Print the art first
    print(ascii_art)
    
    # Then prompt the user for input
    store_url = input("Enter the LINE STORE sticker or emoji pack URL: ")

    if "store.line.me" in store_url:
        download_from_url(store_url)
    else:
        print("Error: Please enter a valid URL from the LINE STORE (store.line.me).")
