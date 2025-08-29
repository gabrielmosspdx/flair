def load_images(self):
    image_files = {
        'floor': 'assets/images/sanfranhotel.png',
        'happy_customer': 'assets/images/happycustomer.png',
        'unhappy_customer': 'assets/images/unhappycustomer.png',
        'beer_icon': 'assets/images/beer.png',
        'wine_icon': 'assets/images/wine.png',
        'cocktail_icon': 'assets/images/cocktail.png'
    }

    for image_name, image_path in image_files.items():
        image = pygame.image.load(image_path)
        if image_name in ['beer_icon', 'wine_icon', 'cocktail_icon']:
            image = pygame.transform.scale(image, (36, 36))
        self.images[image_name] = image


def draw_game_ui(self):
    for drink_type in self.inventory:
        # Calculate x and other relevant variables
        icon_map = {
            DrinkType.BEER: self.images.get('beer_icon'),
            DrinkType.WINE: self.images.get('wine_icon'),
            DrinkType.COCKTAIL: self.images.get('cocktail_icon')
        }
        icon = icon_map.get(drink_type)
        if icon:
            icon_rect = icon.get_rect(center=(x, inv_y))
            self.screen.blit(icon, icon_rect)
        else:
            pygame.draw.circle(self.screen, color, (x, inv_y), 18)