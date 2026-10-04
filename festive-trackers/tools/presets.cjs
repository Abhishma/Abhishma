/*
 * Category templates for D2C stores, and brand starters that point at them.
 * Plain script (no modules): inlined into the published page and loaded by Node, like catalog.cjs.
 *
 * A template sorts products into categories by keywords found in the product type, title and tags.
 * Order matters: categories and sub-categories are tried top to bottom and the first match wins,
 * so specific items (oversized t-shirt) sit above general ones (t-shirt, shirt).
 *
 * Brand starters reflect each brand's public storefront menus as generally known; they are starting
 * points, not the brand's own data, and imply no affiliation. Check them against the live store
 * (and adjust in the CSV) before relying on category numbers.
 *
 * Template shape: { id, name, cats: [[category, [keywords], [[subcategory, [keywords]], ...]], ...],
 *                   focus: [suggested focus-group tags], noStock: [categories that hold no stock] }
 */
var TKPresets = (function () {
  'use strict';
  var GIFT = ['Gift Cards', ['gift card', 'gift voucher', 'e gift'], []];
  var COMBOS = ['Combos and Bundles', ['combo', 'bundle', 'pack of', 'set of', 'kit'], []];

  var TEMPLATES = [
    { id: 'streetwear', name: 'Streetwear and casual wear', focus: ['Bestsellers', 'New launch', 'Sale'], noStock: ['Gift Cards', 'Combos and Bundles'], cats: [
      ['Oversized T-shirts', ['oversized t shirt', 'oversized tee', 'drop shoulder', 'boxy t shirt', 'boxy tee'], [['Graphic', ['graphic', 'printed', 'print']], ['Solid', ['solid', 'plain', 'basic']]]],
      ['T-shirts', ['t shirt', 'tee', 'tshirt', 'henley', 'tank top', 'vest', 'muscle fit'], [['Graphic', ['graphic', 'printed', 'print']], ['Polo', ['polo']], ['Solid', ['solid', 'plain', 'basic']]]],
      ['Hoodies and Sweatshirts', ['hoodie', 'sweatshirt', 'zipper', 'pullover', 'crewneck sweat'], [['Hoodies', ['hoodie', 'hooded']], ['Sweatshirts', ['sweatshirt', 'pullover']]]],
      ['Shirts', ['shirt', 'overshirt', 'shacket'], [['Overshirts and Shackets', ['overshirt', 'shacket']], ['Printed', ['printed', 'print', 'resort', 'hawaiian']], ['Solid', ['solid', 'plain', 'oxford', 'linen']]]],
      ['Co-ord Sets', ['co ord', 'coord', 'matching set', 'two piece set'], []],
      ['Joggers and Trackpants', ['jogger', 'trackpant', 'track pant', 'sweatpant'], []],
      ['Cargo Pants', ['cargo', 'parachute pant', 'utility pant'], []],
      ['Jeans', ['jean', 'denim'], [['Baggy and Wide', ['baggy', 'wide leg', 'relaxed', 'loose']], ['Straight', ['straight']], ['Slim', ['slim', 'skinny', 'tapered']]]],
      ['Trousers', ['trouser', 'pant', 'chino', 'korean pant'], []],
      ['Shorts', ['short', 'boxers short', 'bermuda'], []],
      ['Jackets', ['jacket', 'puffer', 'bomber', 'varsity', 'windcheater', 'coat'], []],
      ['Sweaters', ['sweater', 'cardigan', 'knit'], []],
      ['Women Tops', ['crop top', 'women top', 'baby tee', 'corset', 'bodysuit'], []],
      ['Dresses and Skirts', ['dress', 'skirt'], []],
      ['Footwear', ['sneaker', 'slider', 'slipper', 'flip flop', 'clog', 'shoe'], []],
      ['Accessories', ['cap', 'beanie', 'sock', 'bag', 'tote', 'backpack', 'belt', 'sunglass', 'chain', 'bracelet', 'ring', 'wallet', 'phone cover', 'phone case', 'perfume'], [['Headwear', ['cap', 'beanie', 'hat']], ['Bags', ['bag', 'tote', 'backpack']], ['Jewellery', ['chain', 'bracelet', 'ring', 'pendant']], ['Phone Covers', ['phone cover', 'phone case']]]],
      COMBOS, GIFT,
    ] },
    { id: 'premium-menswear', name: 'Premium menswear', focus: ['Bestsellers', 'New arrivals', 'Wedding edit'], noStock: ['Gift Cards'], cats: [
      ['Polos', ['polo'], []],
      ['T-shirts', ['t shirt', 'tee', 'henley'], []],
      ['Overshirts', ['overshirt', 'shacket'], []],
      ['Shirts', ['shirt'], [['Formal', ['formal', 'office', 'business', 'cutaway']], ['Linen', ['linen']], ['Printed', ['printed', 'print', 'resort']], ['Casual', ['casual', 'oxford', 'corduroy', 'flannel']]]],
      ['Knitwear', ['sweater', 'cardigan', 'knit', 'pullover', 'turtleneck'], []],
      ['Blazers and Suits', ['blazer', 'suit', 'waistcoat', 'nehru jacket', 'bandhgala', 'tuxedo'], []],
      ['Jackets', ['jacket', 'bomber', 'gilet', 'coat', 'trench'], []],
      ['Trousers', ['trouser', 'chino', 'pant', 'pleated', 'gurkha'], [['Formal', ['formal', 'pleated', 'gurkha']], ['Chinos', ['chino']]]],
      ['Jeans', ['jean', 'denim'], []],
      ['Shorts', ['short'], []],
      ['Co-ord Sets', ['co ord', 'coord', 'set'], []],
      ['Ethnic Wear', ['kurta', 'sherwani', 'jodhpuri'], []],
      ['Footwear', ['loafer', 'sneaker', 'derby', 'boot', 'mule', 'shoe'], []],
      ['Accessories', ['belt', 'wallet', 'tie', 'pocket square', 'cufflink', 'sock', 'cap', 'perfume', 'bag'], []],
      GIFT,
    ] },
    { id: 'womenswear-ethnic', name: 'Womenswear and ethnic wear', focus: ['Bestsellers', 'New arrivals', 'Festive edit'], noStock: ['Gift Cards'], cats: [
      ['Kurta Sets', ['kurta set', 'suit set', 'salwar suit', 'anarkali set', 'sharara set', 'palazzo set', 'kurta with'], [['Anarkali', ['anarkali']], ['Sharara and Gharara', ['sharara', 'gharara']], ['Straight', ['straight']]]],
      ['Kurtas and Kurtis', ['kurta', 'kurti', 'tunic'], []],
      ['Sarees', ['saree', 'sari'], [['Silk', ['silk', 'banarasi', 'kanjeevaram']], ['Cotton', ['cotton', 'handloom', 'mulmul']]]],
      ['Lehengas', ['lehenga', 'ghagra', 'chaniya'], []],
      ['Dupattas', ['dupatta', 'stole'], []],
      ['Ethnic Bottoms', ['palazzo', 'salwar', 'churidar', 'dhoti pant', 'patiala'], []],
      ['Dresses', ['dress', 'maxi', 'midi', 'gown', 'jumpsuit'], []],
      ['Tops and Tunics', ['top', 'blouse', 'shirt', 'crop'], []],
      ['Co-ord Sets', ['co ord', 'coord', 'set'], []],
      ['Bottoms', ['trouser', 'pant', 'jean', 'skirt', 'short', 'legging', 'jegging'], []],
      ['Outerwear', ['jacket', 'shrug', 'blazer', 'coat', 'cardigan', 'sweater'], []],
      ['Nightwear and Loungewear', ['nightwear', 'night suit', 'pyjama', 'pajama', 'lounge', 'nightie'], []],
      ['Jewellery and Accessories', ['earring', 'necklace', 'bangle', 'bag', 'clutch', 'potli', 'juttis', 'jutti'], []],
      GIFT,
    ] },
    { id: 'innerwear-athleisure', name: 'Innerwear and athleisure', focus: ['Bestsellers', 'Packs', 'New launch'], noStock: ['Gift Cards'], cats: [
      ['Briefs and Trunks', ['brief', 'trunk'], []],
      ['Boxers', ['boxer'], []],
      ['Vests', ['vest', 'undershirt', 'inner tee'], []],
      ['Bras', ['bra', 'bralette'], [['Sports Bras', ['sports bra']], ['Everyday', ['t shirt bra', 'everyday', 'non padded', 'padded']]]],
      ['Panties', ['panty', 'panties', 'hipster', 'bikini brief', 'boyshort'], []],
      ['Shapewear', ['shapewear', 'shaper', 'tummy'], []],
      ['Activewear Tops', ['sports t shirt', 'active tee', 'gym tee', 'training top', 'tank'], []],
      ['Leggings and Joggers', ['legging', 'jogger', 'trackpant', 'flare pant', 'yoga pant'], []],
      ['Shorts', ['short', 'cycling short'], []],
      ['Loungewear and Sleepwear', ['lounge', 'pyjama', 'pajama', 'sleep', 'night'], []],
      ['Socks', ['sock'], []],
      COMBOS, GIFT,
    ] },
    { id: 'kids-baby', name: 'Baby and kids', focus: ['Bestsellers', 'New launch', 'Gifting'], noStock: ['Gift Cards', 'Combos and Bundles'], cats: [
      ['Strollers and Prams', ['stroller', 'pram', 'buggy'], []],
      ['Car Seats', ['car seat', 'booster seat'], []],
      ['Ride-ons', ['ride on', 'tricycle', 'scooter', 'balance bike', 'cycle', 'rocker'], []],
      ['Toys', ['toy', 'puzzle', 'blocks', 'play gym', 'rattle', 'teether', 'plush'], []],
      ['Nursery and Furniture', ['cot', 'crib', 'cradle', 'bassinet', 'high chair', 'play pen', 'playpen', 'mattress'], []],
      ['Feeding', ['bottle', 'sipper', 'feeding', 'breast pump', 'sterilizer', 'bib', 'nipple'], []],
      ['Diapering', ['diaper', 'wipes', 'nappy', 'changing mat'], []],
      ['Bath and Skin Care', ['bath', 'soap', 'shampoo', 'lotion', 'oil', 'cream', 'powder', 'rash'], []],
      ['Clothing', ['onesie', 'romper', 'bodysuit', 'jabla', 'frock', 'dress', 't shirt', 'shorts', 'pyjama', 'set', 'sleepsuit'], []],
      ['Bedding and Swaddles', ['swaddle', 'blanket', 'wrap', 'quilt', 'pillow', 'bedding'], []],
      ['Carriers', ['carrier', 'hip seat'], []],
      COMBOS, GIFT,
    ] },
    { id: 'footwear', name: 'Footwear', focus: ['Bestsellers', 'New launch', 'Sale'], noStock: ['Gift Cards'], cats: [
      ['Sneakers', ['sneaker', 'trainer', 'high top', 'low top'], []],
      ['Running and Sports', ['running', 'sports shoe', 'walking shoe', 'training shoe'], []],
      ['Loafers and Moccasins', ['loafer', 'moccasin', 'driver'], []],
      ['Formal Shoes', ['derby', 'oxford', 'brogue', 'monk'], []],
      ['Boots', ['boot', 'chelsea', 'chukka'], []],
      ['Sandals', ['sandal', 'kolhapuri', 'gladiator'], []],
      ['Sliders and Flip-flops', ['slider', 'slide', 'flip flop', 'slipper', 'clog'], []],
      ['Heels and Flats', ['heel', 'wedge', 'flat', 'ballerina', 'mule', 'jutti'], []],
      ['Kids Shoes', ['kids', 'boys', 'girls'], []],
      ['Socks and Care', ['sock', 'insole', 'shoe care', 'cleaner', 'lace'], []],
      GIFT,
    ] },
    { id: 'jewellery', name: 'Jewellery and accessories', focus: ['Bestsellers', 'Gifting', 'New launch'], noStock: ['Gift Cards'], cats: [
      ['Earrings', ['earring', 'stud', 'hoop', 'jhumka', 'drop'], []],
      ['Necklaces and Pendants', ['necklace', 'pendant', 'chain', 'choker', 'mangalsutra'], []],
      ['Rings', ['ring'], []],
      ['Bracelets and Bangles', ['bracelet', 'bangle', 'kada', 'cuff'], []],
      ['Anklets', ['anklet', 'payal'], []],
      ['Nose Pins', ['nose pin', 'nose ring', 'nath'], []],
      ['Jewellery Sets', ['set', 'combo'], []],
      ['Men Jewellery', ['men', 'mens'], []],
      ['Watches', ['watch'], []],
      ['Hair Accessories', ['clip', 'claw', 'scrunchie', 'hairband', 'hair'], []],
      ['Bags', ['bag', 'tote', 'sling', 'clutch', 'wallet'], []],
      GIFT,
    ] },
    { id: 'beauty', name: 'Beauty and personal care', focus: ['Bestsellers', 'New launch', 'Value packs'], noStock: ['Gift Cards', 'Combos and Bundles'], cats: [
      ['Face Care', ['face wash', 'cleanser', 'serum', 'moisturizer', 'moisturiser', 'toner', 'face mask', 'sunscreen', 'spf', 'face cream', 'night cream', 'eye cream', 'exfoliat'], [['Sunscreen', ['sunscreen', 'spf']], ['Serums', ['serum']], ['Cleansers', ['face wash', 'cleanser']], ['Moisturisers', ['moisturizer', 'moisturiser', 'cream']]]],
      ['Hair Care', ['shampoo', 'conditioner', 'hair oil', 'hair mask', 'hair serum', 'onion'], []],
      ['Body Care', ['body wash', 'body lotion', 'body butter', 'soap', 'scrub', 'deodorant', 'roll on'], []],
      ['Lips', ['lipstick', 'lip balm', 'lip gloss', 'lip liner', 'lip tint', 'lip crayon'], []],
      ['Eyes', ['kajal', 'eyeliner', 'mascara', 'eyeshadow', 'eye shadow', 'brow'], []],
      ['Face Makeup', ['foundation', 'concealer', 'compact', 'primer', 'blush', 'highlighter', 'bronzer', 'setting', 'bb cream', 'cc cream'], []],
      ['Nails', ['nail'], []],
      ['Fragrance', ['perfume', 'eau de', 'edp', 'edt', 'body mist', 'attar'], []],
      ['Men Grooming', ['beard', 'shaving', 'trimmer', 'aftershave', 'men'], []],
      ['Baby Care', ['baby'], []],
      ['Tools and Accessories', ['brush', 'sponge', 'blender', 'roller', 'gua sha', 'tool'], []],
      COMBOS, GIFT,
    ] },
    { id: 'fragrance', name: 'Fragrances', focus: ['Bestsellers', 'Gift sets', 'New launch'], noStock: ['Gift Cards'], cats: [
      ['Gift Sets', ['gift set', 'combo', 'kit', 'discovery set', 'pack of'], []],
      ['Perfumes', ['perfume', 'eau de parfum', 'edp', 'eau de toilette', 'edt', 'parfum', 'cologne'], [['Men', ['men', 'him']], ['Women', ['women', 'her']], ['Unisex', ['unisex']]]],
      ['Body Mists and Deodorants', ['body mist', 'deodorant', 'deo', 'body spray'], []],
      ['Attars', ['attar', 'ittar', 'oud'], []],
      ['Home Fragrance', ['candle', 'diffuser', 'room spray', 'incense'], []],
      ['Bath and Body', ['body wash', 'lotion', 'soap'], []],
      GIFT,
    ] },
    { id: 'health-nutrition', name: 'Health and nutrition', focus: ['Bestsellers', 'Subscriptions', 'New launch'], noStock: ['Gift Cards', 'Combos and Bundles'], cats: [
      ['Protein', ['protein', 'whey', 'plant protein', 'mass gainer'], []],
      ['Vitamins and Supplements', ['vitamin', 'multivitamin', 'omega', 'biotin', 'collagen', 'calcium', 'iron', 'zinc', 'magnesium', 'tablet', 'capsule', 'effervescent'], []],
      ['Ayurveda and Herbal', ['ashwagandha', 'shilajit', 'triphala', 'ayurved', 'herbal', 'juice', 'churna'], []],
      ['Gummies', ['gummy', 'gummies'], []],
      ['Weight Management', ['weight', 'slim', 'apple cider', 'fat'], []],
      ['Sports Nutrition', ['pre workout', 'bcaa', 'creatine', 'electrolyte', 'energy'], []],
      ['Healthy Snacks', ['bar', 'muesli', 'granola', 'peanut butter', 'oats', 'snack'], []],
      ['Women Health', ['pcos', 'period', 'women', 'prenatal'], []],
      COMBOS, GIFT,
    ] },
    { id: 'food-beverage', name: 'Food and beverages', focus: ['Bestsellers', 'Subscriptions', 'New launch'], noStock: ['Gift Cards', 'Combos and Bundles'], cats: [
      ['Coffee', ['coffee', 'cold brew', 'espresso', 'drip bag', 'filter'], [['Instant', ['instant']], ['Cold Brew', ['cold brew']], ['Ground and Beans', ['ground', 'beans', 'roast']]]],
      ['Tea', ['tea', 'chai', 'matcha', 'green tea'], []],
      ['Snacks', ['chips', 'namkeen', 'makhana', 'nuts', 'trail mix', 'cookie', 'biscuit', 'snack'], []],
      ['Spreads', ['peanut butter', 'spread', 'jam', 'honey', 'nutella'], []],
      ['Breakfast', ['muesli', 'granola', 'oats', 'cereal'], []],
      ['Bars', ['bar'], []],
      ['Chocolates and Sweets', ['chocolate', 'mithai', 'sweet', 'candy'], []],
      ['Beverages', ['juice', 'drink', 'soda', 'kombucha', 'water'], []],
      ['Pantry', ['masala', 'spice', 'ghee', 'oil', 'flour', 'atta', 'rice', 'pickle', 'sauce'], []],
      ['Equipment', ['french press', 'grinder', 'mug', 'brewer', 'kettle', 'pour over'], []],
      COMBOS, GIFT,
    ] },
    { id: 'home-sleep', name: 'Home, sleep and furniture', focus: ['Bestsellers', 'New launch', 'Sale'], noStock: ['Gift Cards'], cats: [
      ['Mattresses', ['mattress'], [['Memory Foam', ['memory foam']], ['Orthopaedic', ['ortho']], ['Latex', ['latex']]]],
      ['Pillows', ['pillow'], []],
      ['Bedding', ['bedsheet', 'bed sheet', 'comforter', 'duvet', 'quilt', 'dohar', 'blanket', 'mattress protector'], []],
      ['Beds', ['bed', 'cot'], []],
      ['Sofas and Seating', ['sofa', 'recliner', 'chair', 'bean bag', 'ottoman', 'pouf'], []],
      ['Tables', ['table', 'desk'], []],
      ['Storage', ['wardrobe', 'cabinet', 'shelf', 'rack', 'drawer', 'storage'], []],
      ['Kitchen and Dining', ['cookware', 'pan', 'kadai', 'tawa', 'pressure cooker', 'dinner set', 'plate', 'bowl', 'glass', 'bottle', 'container'], []],
      ['Bath', ['towel', 'bath mat', 'bathrobe'], []],
      ['Home Decor', ['lamp', 'vase', 'mirror', 'wall art', 'clock', 'candle', 'planter', 'cushion'], []],
      GIFT,
    ] },
    { id: 'rugs-decor', name: 'Rugs and home decor', focus: ['Bestsellers', 'New collection', 'Ready to ship'], noStock: ['Gift Cards', 'Services'], cats: [
      ['Rugs', ['rug', 'carpet', 'dhurrie', 'kilim', 'runner'], [['Hand-knotted', ['hand knotted', 'handknotted']], ['Hand-tufted', ['hand tufted', 'tufted']], ['Flatweave', ['flatweave', 'flat weave', 'dhurrie', 'kilim']], ['Runners', ['runner']], ['Outdoor', ['outdoor']]]],
      ['Cushions', ['cushion', 'pillow cover', 'cushion cover'], []],
      ['Throws and Blankets', ['throw', 'blanket'], []],
      ['Bedding', ['bedsheet', 'bed sheet', 'duvet', 'quilt', 'bedspread', 'bed cover'], []],
      ['Curtains and Upholstery', ['curtain', 'drape', 'upholstery', 'fabric'], []],
      ['Wallcoverings', ['wallpaper', 'wall covering', 'wallcovering'], []],
      ['Lighting', ['lamp', 'pendant', 'chandelier', 'light', 'sconce'], []],
      ['Furniture', ['chair', 'sofa', 'table', 'stool', 'bench', 'ottoman', 'pouf'], []],
      ['Tableware', ['dinnerware', 'plate', 'bowl', 'mug', 'table linen', 'placemat', 'napkin', 'table runner'], []],
      ['Decor Accents', ['vase', 'mirror', 'candle', 'tray', 'basket', 'wall art', 'sculpture'], []],
      ['Services', ['custom', 'swatch', 'sample', 'consultation'], []],
      GIFT,
    ] },
    { id: 'electronics-audio', name: 'Consumer electronics and audio', focus: ['Bestsellers', 'New launch', 'Deals'], noStock: ['Gift Cards'], cats: [
      ['True Wireless Earbuds', ['earbud', 'tws', 'airdopes', 'true wireless'], []],
      ['Neckbands', ['neckband'], []],
      ['Headphones', ['headphone', 'over ear', 'on ear', 'rockerz'], []],
      ['Wired Earphones', ['wired', 'earphone', 'bassheads'], []],
      ['Smartwatches', ['smartwatch', 'smart watch', 'watch'], []],
      ['Speakers', ['speaker', 'soundbar', 'stone', 'party'], []],
      ['Power Banks', ['power bank', 'powerbank'], []],
      ['Chargers and Cables', ['charger', 'cable', 'adapter'], []],
      ['Smart Rings and Fitness', ['smart ring', 'ring', 'fitness band'], []],
      ['Accessories', ['case', 'strap', 'cover', 'stand'], []],
      GIFT,
    ] },
    { id: 'bags-travel', name: 'Bags and travel', focus: ['Bestsellers', 'New launch', 'Sets'], noStock: ['Gift Cards'], cats: [
      ['Luggage Sets', ['set of', 'luggage set', 'trolley set'], []],
      ['Cabin Luggage', ['cabin'], []],
      ['Check-in Luggage', ['check in', 'checkin', 'large', 'medium'], []],
      ['Backpacks', ['backpack', 'laptop bag'], []],
      ['Duffles', ['duffle', 'duffel', 'weekender', 'gym bag'], []],
      ['Handbags and Totes', ['tote', 'handbag', 'sling', 'crossbody', 'satchel'], []],
      ['Wallets and Small Goods', ['wallet', 'card holder', 'passport', 'pouch', 'organiser', 'organizer'], []],
      ['Travel Accessories', ['luggage tag', 'neck pillow', 'cover', 'lock', 'packing cube'], []],
      GIFT,
    ] },
    { id: 'pet', name: 'Pet supplies', focus: ['Bestsellers', 'New launch', 'Subscriptions'], noStock: ['Gift Cards', 'Services'], cats: [
      ['Dog Food', ['dog food', 'puppy food', 'kibble'], []],
      ['Cat Food', ['cat food', 'kitten food'], []],
      ['Treats', ['treat', 'chew', 'jerky', 'biscuit'], []],
      ['Toys', ['toy', 'ball', 'rope'], []],
      ['Collars, Leashes and Harnesses', ['collar', 'leash', 'harness'], []],
      ['Beds and Mats', ['bed', 'mat', 'cushion'], []],
      ['Grooming', ['shampoo', 'brush', 'comb', 'grooming', 'wipes'], []],
      ['Bowls and Feeders', ['bowl', 'feeder', 'fountain'], []],
      ['Health and Supplements', ['supplement', 'tick', 'flea', 'deworm', 'vitamin'], []],
      ['Litter and Hygiene', ['litter', 'poop', 'diaper', 'pad'], []],
      ['Apparel', ['jacket', 't shirt', 'bandana', 'costume', 'sweater'], []],
      ['Services', ['grooming session', 'vet', 'consultation', 'training'], []],
      GIFT,
    ] },
    { id: 'kitchenware', name: 'Kitchenware and appliances', focus: ['Bestsellers', 'New launch', 'Gifting'], noStock: ['Gift Cards'], cats: [
      ['Cookware', ['kadai', 'tawa', 'pan', 'pot', 'cookware', 'pressure cooker', 'casserole', 'dosa'], [['Cast Iron', ['cast iron']], ['Stainless Steel', ['stainless', 'steel', 'triply', 'tri ply']], ['Non-stick', ['non stick', 'nonstick']]]],
      ['Small Appliances', ['mixer', 'grinder', 'blender', 'kettle', 'toaster', 'air fryer', 'induction', 'juicer', 'chopper'], []],
      ['Serveware and Dinnerware', ['plate', 'bowl', 'dinner set', 'serving', 'thali', 'cup', 'mug', 'glass'], []],
      ['Storage', ['container', 'jar', 'lunch box', 'tiffin', 'bottle', 'flask'], []],
      ['Tools and Utensils', ['knife', 'ladle', 'spatula', 'peeler', 'board', 'grater', 'whisk', 'tong'], []],
      ['Bakeware', ['bake', 'mould', 'mold', 'tray', 'oven'], []],
      COMBOS, GIFT,
    ] },
    { id: 'eyewear', name: 'Eyewear', focus: ['Bestsellers', 'New launch', 'Blue light'], noStock: ['Gift Cards', 'Services'], cats: [
      ['Sunglasses', ['sunglass', 'shades', 'aviator', 'wayfarer'], []],
      ['Eyeglasses', ['eyeglass', 'frame', 'spectacle', 'optical'], []],
      ['Computer Glasses', ['blue light', 'blu', 'computer glass', 'screen'], []],
      ['Contact Lenses', ['contact lens', 'lens'], []],
      ['Kids Eyewear', ['kids'], []],
      ['Accessories', ['case', 'cleaner', 'chain', 'cord', 'cloth'], []],
      ['Services', ['eye test', 'lens upgrade', 'power'], []],
      GIFT,
    ] },
    { id: 'ethnic-menswear', name: 'Ethnic and occasion menswear', focus: ['Bestsellers', 'Wedding edit', 'Festive edit'], noStock: ['Gift Cards'], cats: [
      ['Sherwanis', ['sherwani', 'achkan'], []],
      ['Kurta Sets', ['kurta set', 'kurta pyjama', 'kurta with'], []],
      ['Kurtas', ['kurta'], []],
      ['Nehru Jackets', ['nehru jacket', 'bandi', 'modi jacket'], []],
      ['Indo-western', ['indo western', 'indowestern', 'jodhpuri', 'bandhgala'], []],
      ['Ethnic Bottoms', ['pyjama', 'churidar', 'dhoti', 'patiala'], []],
      ['Footwear', ['mojari', 'jutti', 'nagra', 'kolhapuri'], []],
      ['Accessories', ['safa', 'turban', 'stole', 'brooch', 'mala', 'pocket square'], []],
      ['Kids Ethnic', ['kids', 'boys'], []],
      GIFT,
    ] },
    { id: 'mens-grooming', name: 'Men\'s grooming', focus: ['Bestsellers', 'Kits', 'New launch'], noStock: ['Gift Cards', 'Combos and Bundles'], cats: [
      ['Beard Care', ['beard oil', 'beard wash', 'beard balm', 'beard growth', 'beard'], []],
      ['Shaving', ['razor', 'shaving cream', 'shaving foam', 'shave gel', 'blade', 'after shave', 'aftershave'], []],
      ['Trimmers and Devices', ['trimmer', 'shaver', 'grooming kit device', 'hair clipper'], []],
      ['Hair Styling', ['hair wax', 'pomade', 'hair gel', 'hair clay', 'hair spray'], []],
      ['Hair Care', ['shampoo', 'conditioner', 'hair oil', 'anti dandruff', 'hair fall'], []],
      ['Face Care', ['face wash', 'face scrub', 'moisturizer', 'moisturiser', 'sunscreen', 'charcoal', 'serum'], []],
      ['Body Care', ['body wash', 'soap', 'body lotion', 'talc', 'deodorant', 'deo'], []],
      ['Fragrance', ['perfume', 'edp', 'edt', 'cologne', 'body spray'], []],
      ['Intimate Hygiene', ['intimate', 'groin'], []],
      COMBOS, GIFT,
    ] },
    { id: 'sports-fitness', name: 'Sports and fitness', focus: ['Bestsellers', 'Home gym', 'New launch'], noStock: ['Gift Cards'], cats: [
      ['Home Gym Equipment', ['dumbbell', 'kettlebell', 'barbell', 'weight plate', 'bench', 'treadmill', 'exercise bike', 'cycle', 'pull up bar', 'home gym'], []],
      ['Yoga and Pilates', ['yoga mat', 'yoga block', 'yoga strap', 'pilates', 'mat'], []],
      ['Resistance and Recovery', ['resistance band', 'loop band', 'foam roller', 'massager', 'massage gun'], []],
      ['Cardio Accessories', ['skipping rope', 'jump rope', 'ab roller', 'push up bar', 'gripper'], []],
      ['Sports Gear', ['football', 'cricket', 'badminton', 'racket', 'racquet', 'shuttle', 'tennis', 'basketball', 'volleyball', 'bat', 'ball'], []],
      ['Activewear', ['gym t shirt', 'track pant', 'jogger', 'sports bra', 'legging', 'shorts', 'tank', 'jersey'], []],
      ['Gym Accessories', ['gym bag', 'gloves', 'belt', 'shaker', 'bottle', 'towel', 'wrist band', 'knee cap', 'support'], []],
      ['Smart Fitness', ['smart', 'tracker', 'scale'], []],
      GIFT,
    ] },
    { id: 'watches', name: 'Watches', focus: ['Bestsellers', 'New launch', 'Gifting'], noStock: ['Gift Cards'], cats: [
      ['Smartwatches', ['smartwatch', 'smart watch', 'fitness band', 'smart band'], []],
      ['Men Watches', ['men', 'mens', 'gents'], [['Chronograph', ['chronograph']], ['Automatic', ['automatic', 'mechanical']], ['Analog', ['analog', 'analogue']]]],
      ['Women Watches', ['women', 'womens', 'ladies'], []],
      ['Couple Watches', ['couple', 'pair'], []],
      ['Kids Watches', ['kids', 'boys', 'girls'], []],
      ['Straps', ['strap', 'band', 'bracelet'], []],
      ['Watches', ['watch'], []],
      GIFT,
    ] },
    { id: 'gifting', name: 'Gifting, flowers and stationery', focus: ['Bestsellers', 'Same day', 'Personalised'], noStock: ['Gift Cards'], cats: [
      ['Flowers', ['bouquet', 'roses', 'rose', 'lilies', 'orchid', 'carnation', 'flower'], []],
      ['Cakes', ['cake', 'cupcake', 'pastry'], []],
      ['Personalised Gifts', ['personalised', 'personalized', 'custom', 'photo', 'name'], []],
      ['Hampers', ['hamper', 'gift box', 'basket'], []],
      ['Chocolates and Sweets', ['chocolate', 'sweet', 'mithai', 'dry fruit'], []],
      ['Plants', ['plant', 'bonsai', 'succulent'], []],
      ['Stationery', ['notebook', 'diary', 'journal', 'planner', 'pen', 'sticker', 'bookmark'], []],
      ['Home and Decor', ['mug', 'cushion', 'lamp', 'candle', 'frame', 'clock', 'decor', 'coaster', 'magnet'], []],
      ['Bags and Accessories', ['bag', 'tote', 'wallet', 'keychain', 'pouch', 'sling'], []],
      ['Soft Toys', ['teddy', 'soft toy', 'plush'], []],
      GIFT,
    ] },
    { id: 'plants-garden', name: 'Plants and gardening', focus: ['Bestsellers', 'Low maintenance', 'Gifting'], noStock: ['Gift Cards', 'Services'], cats: [
      ['Indoor Plants', ['indoor', 'snake plant', 'money plant', 'pothos', 'zz plant', 'monstera', 'peace lily', 'areca', 'jade', 'fern'], []],
      ['Outdoor and Flowering', ['outdoor', 'flowering', 'hibiscus', 'bougainvillea', 'rose plant', 'jasmine'], []],
      ['Succulents and Cacti', ['succulent', 'cactus', 'cacti'], []],
      ['Seeds and Bulbs', ['seed', 'bulb', 'microgreen'], []],
      ['Pots and Planters', ['pot', 'planter', 'hanging basket', 'stand'], []],
      ['Soil and Fertilisers', ['soil', 'potting mix', 'cocopeat', 'fertiliser', 'fertilizer', 'compost', 'manure', 'vermicompost'], []],
      ['Garden Tools', ['tool', 'pruner', 'trowel', 'sprayer', 'watering can', 'gloves', 'hose'], []],
      ['Plant Care', ['neem oil', 'pesticide', 'plant food', 'mist'], []],
      ['Services', ['garden setup', 'maintenance visit', 'consultation'], []],
      GIFT,
    ] },
    { id: 'toys-games', name: 'Toys and games', focus: ['Bestsellers', 'Age 3 to 5', 'New launch'], noStock: ['Gift Cards'], cats: [
      ['STEM and Science Kits', ['stem', 'science', 'robot', 'coding', 'experiment', 'circuit', 'engineering'], []],
      ['Board Games', ['board game', 'card game', 'chess', 'ludo', 'monopoly', 'strategy game'], []],
      ['Puzzles', ['puzzle', 'jigsaw'], []],
      ['Arts and Crafts', ['art', 'craft', 'colouring', 'coloring', 'clay', 'dough', 'paint', 'diy'], []],
      ['Building and Construction', ['blocks', 'building', 'construction', 'magnetic tiles', 'lego'], []],
      ['Pretend Play', ['kitchen set', 'doctor set', 'pretend', 'doll house', 'tool set', 'role play'], []],
      ['Dolls and Soft Toys', ['doll', 'soft toy', 'plush', 'teddy'], []],
      ['Vehicles and Remote Control', ['car', 'truck', 'remote control', 'rc ', 'train', 'helicopter'], []],
      ['Outdoor Play', ['slide', 'swing', 'ball', 'water gun', 'scooter', 'kite'], []],
      ['Baby and Toddler', ['rattle', 'teether', 'stacker', 'sorter', 'baby', 'toddler'], []],
      GIFT,
    ] },
  ];

  /* Brand starters: [brand, template id, focus-group tags or null for the template's]. */
  var BRANDS = [
    ['Bonkers Corner', 'streetwear', null],
    ['The Bear House', 'premium-menswear', null],
    ['Snitch', 'streetwear', null],
    ['The Souled Store', 'streetwear', ['Bestsellers', 'Official merch', 'New launch']],
    ['Bewakoof', 'streetwear', null],
    ['Powerlook', 'streetwear', null],
    ['Urban Monkey', 'streetwear', null],
    ['Nobero', 'streetwear', null],
    ['Rare Rabbit', 'premium-menswear', null],
    ['Andamen', 'premium-menswear', null],
    ['Bombay Shirt Company', 'premium-menswear', null],
    ['Libas', 'womenswear-ethnic', null],
    ['FableStreet', 'womenswear-ethnic', null],
    ['Berrylush', 'womenswear-ethnic', null],
    ['Suta', 'womenswear-ethnic', null],
    ['House of Masaba', 'womenswear-ethnic', null],
    ['XYXX', 'innerwear-athleisure', null],
    ['Bummer', 'innerwear-athleisure', null],
    ['Damensch', 'innerwear-athleisure', null],
    ['Blissclub', 'innerwear-athleisure', null],
    ['Clovia', 'innerwear-athleisure', null],
    ['R for Rabbit', 'kids-baby', null],
    ['Neeman\'s', 'footwear', null],
    ['Comet', 'footwear', null],
    ['Bacca Bucci', 'footwear', null],
    ['Giva', 'jewellery', null],
    ['Salty', 'jewellery', null],
    ['Palmonas', 'jewellery', null],
    ['Mamaearth', 'beauty', null],
    ['Sugar Cosmetics', 'beauty', null],
    ['Minimalist', 'beauty', null],
    ['Plum', 'beauty', null],
    ['The Derma Co', 'beauty', null],
    ['Bella Vita', 'fragrance', null],
    ['Oziva', 'health-nutrition', null],
    ['Wellbeing Nutrition', 'health-nutrition', null],
    ['Kapiva', 'health-nutrition', null],
    ['The Whole Truth', 'food-beverage', null],
    ['Sleepy Owl', 'food-beverage', null],
    ['Blue Tokai', 'food-beverage', null],
    ['Rage Coffee', 'food-beverage', null],
    ['Wakefit', 'home-sleep', null],
    ['The Sleep Company', 'home-sleep', null],
    ['Jaipur Rugs', 'rugs-decor', null],
    ['Shyam Ahuja', 'rugs-decor', null],
    ['Asterlane', 'rugs-decor', null],
    ['boAt', 'electronics-audio', null],
    ['Noise', 'electronics-audio', null],
    ['Boult', 'electronics-audio', null],
    ['Mokobara', 'bags-travel', null],
    ['Nasher Miles', 'bags-travel', null],
    ['Uppercase', 'bags-travel', null],
    ['Heads Up For Tails', 'pet', null],
    ['Supertails', 'pet', null],
    ['The Indus Valley', 'kitchenware', null],
    ['Wonderchef', 'kitchenware', null],
    ['John Jacobs', 'eyewear', null],
    // Added: more apparel, beauty, nutrition, food, home, electronics and new verticals.
    ['Freakins', 'streetwear', null],
    ['Rigo', 'streetwear', null],
    ['The Pant Project', 'premium-menswear', null],
    ['Bunaai', 'womenswear-ethnic', null],
    ['Jaypore', 'womenswear-ethnic', null],
    ['Kalki Fashion', 'womenswear-ethnic', null],
    ['Manyavar', 'ethnic-menswear', null],
    ['Tasva', 'ethnic-menswear', null],
    ['Miniklub', 'kids-baby', null],
    ['The Mom\'s Co', 'kids-baby', null],
    ['Mother Sparsh', 'kids-baby', null],
    ['Campus', 'footwear', null],
    ['CaratLane', 'jewellery', null],
    ['Melorra', 'jewellery', null],
    ['mCaffeine', 'beauty', null],
    ['Pilgrim', 'beauty', null],
    ['WOW Skin Science', 'beauty', null],
    ['Dot and Key', 'beauty', null],
    ['Foxtale', 'beauty', null],
    ['Beardo', 'mens-grooming', null],
    ['Bombay Shaving Company', 'mens-grooming', null],
    ['Ustraa', 'mens-grooming', null],
    ['The Man Company', 'mens-grooming', null],
    ['Skinn', 'fragrance', null],
    ['MuscleBlaze', 'health-nutrition', null],
    ['Fast and Up', 'health-nutrition', null],
    ['Man Matters', 'health-nutrition', null],
    ['Yogabar', 'food-beverage', null],
    ['Farmley', 'food-beverage', null],
    ['Paper Boat', 'food-beverage', null],
    ['Slurrp Farm', 'food-beverage', null],
    ['Duroflex', 'home-sleep', null],
    ['Sleepyhead', 'home-sleep', null],
    ['Fire-Boltt', 'electronics-audio', null],
    ['pTron', 'electronics-audio', null],
    ['Portronics', 'electronics-audio', null],
    ['Zouk', 'bags-travel', null],
    ['Assembly', 'bags-travel', null],
    ['Wiggles', 'pet', null],
    ['Borosil', 'kitchenware', null],
    ['Lenskart', 'eyewear', null],
    ['Boldfit', 'sports-fitness', null],
    ['Cultsport', 'sports-fitness', null],
    ['Nivia', 'sports-fitness', null],
    ['Fastrack', 'watches', null],
    ['Titan', 'watches', null],
    ['Sylvi', 'watches', null],
    ['Chumbak', 'gifting', null],
    ['IGP', 'gifting', null],
    ['Ferns N Petals', 'gifting', null],
    ['Ugaoo', 'plants-garden', null],
    ['Nurserylive', 'plants-garden', null],
    ['Smartivity', 'toys-games', null],
    ['Skillmatics', 'toys-games', null],
    ['Funskool', 'toys-games', null],
  ];

  var byId = {}; TEMPLATES.forEach(function (t) { byId[t.id] = t; });

  /* Lower case, punctuation to spaces, padded, so " t shirt " matches "T-Shirt" and "t-shirts". */
  function norm(s) { return ' ' + String(s || '').toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, ' ').trim() + ' '; }
  function hit(text, kws) {
    for (var i = 0; i < kws.length; i++) {
      var k = norm(kws[i]).trim();
      if (!k) continue;
      if (text.indexOf(' ' + k + ' ') >= 0 || text.indexOf(' ' + k + 's ') >= 0 || text.indexOf(' ' + k + 'es ') >= 0) return true;
      if (k.length >= 6 && text.indexOf(' ' + k) >= 0) return true;   // long stems: "exfoliat", "moisturizer" in "moisturizers"
    }
    return false;
  }

  /* [category, subcategory] for one product, or ['Unmapped', ''] when nothing matches.
     Product type is checked first (most reliable), then title, then tags. */
  function classify(t, productType, title, tags) {
    var fields = [norm(productType), norm(title), norm((tags || []).join(' , '))];
    for (var f = 0; f < fields.length; f++) {
      for (var i = 0; i < t.cats.length; i++) {
        var c = t.cats[i];
        if (!hit(fields[f], c[1])) continue;
        var all = norm(productType + ' ' + title + ' ' + (tags || []).join(' '));
        for (var j = 0; j < c[2].length; j++) if (hit(all, c[2][j][1])) return [c[0], c[2][j][0]];
        return [c[0], ''];
      }
    }
    return ['Unmapped', ''];
  }

  function template(id) {
    var t = byId[id];
    if (t) return t;
    for (var i = 0; i < BRANDS.length; i++) if (slug(BRANDS[i][0]) === id) return byId[BRANDS[i][1]];
    return null;
  }
  function slug(s) { return 'brand:' + String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }

  /* Options for a picker: templates, then brand starters. */
  function choices() {
    return {
      templates: TEMPLATES.map(function (t) { return { id: t.id, name: t.name }; }),
      brands: BRANDS.map(function (b) { return { id: slug(b[0]), name: b[0], template: b[1], templateName: byId[b[1]].name }; }),
    };
  }
  /* Defaults a choice brings: store name, focus tags, no-stock categories. */
  function defaults(id) {
    var t = template(id); if (!t) return null;
    var brand = null; BRANDS.forEach(function (b) { if (slug(b[0]) === id) brand = b; });
    return { name: brand ? brand[0] : '', focusTags: (brand && brand[2]) || t.focus.slice(), noStockCats: t.noStock.slice(), cats: t.cats.map(function (c) { return c[0]; }) };
  }

  return { TEMPLATES: TEMPLATES, BRANDS: BRANDS, classify: classify, template: template, choices: choices, defaults: defaults, slug: slug, norm: norm };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = TKPresets;
