
import json
import os
import hashlib
import base64
import logging
from io import BytesIO
from PIL import Image
import requests

logger = logging.getLogger('pokemon-identifier')

class PokemonDatabase:
    def __init__(self, database_file='pokemon_database.json'):
        self.database_file = database_file
        self.database = self._load_database()
        
    def _load_database(self):
        """Load the Pokemon database from a file or create a new one"""
        try:
            if os.path.exists(self.database_file):
                with open(self.database_file, 'r') as f:
                    return json.load(f)
            else:
                # Create a new database structure
                database = {
                    "image_hashes": {},  # Maps image hashes to Pokemon names
                    "pokemon": {}        # Maps Pokemon names to additional info
                }
                self._save_database(database)
                return database
        except Exception as e:
            logger.error(f"Error loading Pokemon database: {e}")
            return {"image_hashes": {}, "pokemon": {}}
    
    def _save_database(self, database=None):
        """Save the Pokemon database to a file"""
        if database is None:
            database = self.database
        try:
            with open(self.database_file, 'w') as f:
                json.dump(database, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving Pokemon database: {e}")
            return False
    
    async def download_image(self, url):
        """Download an image from a URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None
    
    def _compute_image_hash(self, image):
        """Compute a hash for an image to use as a unique identifier"""
        try:
            # Resize image to normalize it (reduces hash sensitivity to size)
            image = image.resize((100, 100))
            # Convert to grayscale to focus on shape rather than color
            image = image.convert('L')
            
            # Get image data as bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Compute hash
            hash_obj = hashlib.sha256(img_byte_arr)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error computing image hash: {e}")
            return None
    
    async def identify_pokemon(self, image_url):
        """Identify a Pokemon from its image URL using the database"""
        try:
            # Download the image
            image = await self.download_image(image_url)
            if image is None:
                return None, "Could not download the image."
            
            # Compute hash for the image
            image_hash = self._compute_image_hash(image)
            if image_hash is None:
                return None, "Could not compute image hash."
            
            # Check if we have this image hash in our database
            if image_hash in self.database["image_hashes"]:
                pokemon_name = self.database["image_hashes"][image_hash]
                return pokemon_name, f"I think this is a {pokemon_name}!"
            
            # If we don't have this image in our database
            return None, "I don't recognize this Pokemon yet. If you know what it is, use !learn [pokemon_name] to teach me!"
        
        except Exception as e:
            logger.error(f"Error identifying Pokemon: {e}")
            return None, f"Error identifying Pokemon: {e}"
    
    async def learn_pokemon(self, image_url, pokemon_name):
        """Associate an image with a Pokemon name and save it to the database"""
        try:
            # Download the image
            image = await self.download_image(image_url)
            if image is None:
                return False, "Could not download the image."
            
            # Compute hash for the image
            image_hash = self._compute_image_hash(image)
            if image_hash is None:
                return False, "Could not compute image hash."
            
            # Add to our database
            self.database["image_hashes"][image_hash] = pokemon_name
            
            # If this is a new Pokemon, add it to the pokemon dictionary
            if pokemon_name not in self.database["pokemon"]:
                self.database["pokemon"][pokemon_name] = {
                    "count": 1,  # Number of images we have for this Pokemon
                    "first_seen": "now"  # This should be a timestamp in a real implementation
                }
            else:
                self.database["pokemon"][pokemon_name]["count"] += 1
            
            # Save the updated database
            if self._save_database():
                return True, f"Thanks! I've learned that this is a {pokemon_name}."
            else:
                return False, "Failed to save the database."
        
        except Exception as e:
            logger.error(f"Error learning Pokemon: {e}")
            return False, f"Error learning Pokemon: {e}"
    
    def get_known_pokemon(self):
        """Get a list of all Pokemon names in the database"""
        return list(self.database["pokemon"].keys())
    
    def get_pokemon_info(self, pokemon_name):
        """Get information about a Pokemon by name"""
        return self.database["pokemon"].get(pokemon_name, None)