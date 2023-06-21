import os 
from MyBacteriaSite.models import MicrobePost, Profile, Microbe
from django.core.management.base import BaseCommand, CommandError
from PIL import Image
from io import BytesIO
import os
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
import numpy as np
from decimal import Decimal
import random
import string
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


main_path = os.path.join(BASE_DIR, 'static','images','samples')

dirs = os.listdir(main_path)

def random_microbe():
    microbes = Microbe.objects.all()
    index = np.random.randint(0, len(microbes) -1)
    return microbes[index]


def random_profile():
    profiles = Profile.objects.all()
    index = np.random.randint(0, len(profiles) -1)
    return profiles[index].user

def random_coord(x):
    coord = np.random.uniform(0, x)
    coord = np.around(coord, 3)
    return Decimal(coord)
    
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_random_image(main_path, dirs):
    index = np.random.randint(0, len(dirs) -1)
    path = os.path.join(main_path, dirs[index])

    return ImageFile(open(path, "rb")) 

def get_random_likes(post):
    profiles = Profile.objects.all()
    if np.random.randint(0,100) < 50:
        num_of_likes = np.random.randint(0, len(profiles) -1)
        for i in range(num_of_likes):
            profiles[i].user
            post.likes.add(profiles[i].user)
    return post


class Command(BaseCommand):
    help = "Create posts"

    def add_arguments(self, parser):
        parser.add_argument("N", type=int)

    def handle(self, *args, **options):
        for i in range(options['N']):
            post = MicrobePost.objects.create(
                author = random_profile(),
                microbe = random_microbe(),
                title = get_random_string(50),
                longitude = random_coord(180),
                latitude = random_coord(90),
                image = get_random_image(main_path, dirs),
                text = get_random_string(100)
                )
            post = get_random_likes(post)
            print('Created post: ', post)