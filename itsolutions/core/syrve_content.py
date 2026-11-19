"""Copy for the Syrve landing page (core:syrve)."""

WHY = [
    {"icon": "bi-sliders", "title": "Flexible set-up",
     "text": "Menus, taxes, printers, roles and service flow are configured around how your "
             "restaurant actually works, not the other way round."},
    {"icon": "bi-hand-thumbs-up", "title": "Happier guests",
     "text": "Loyalty, offers and guest history in one place help you recognise regulars "
             "and bring them back more often."},
    {"icon": "bi-rocket-takeoff", "title": "More sales per table",
     "text": "Faster ordering, upsell prompts for staff and clear kitchen tickets lift the "
             "average bill without extra effort."},
    {"icon": "bi-graph-up-arrow", "title": "Reports you can act on",
     "text": "Live sales, stock, cost of goods and staff performance on any device, so "
             "decisions are based on numbers, not guesses."},
]

FITS = [
    "Restaurants and bars",
    "Delivery and dark kitchens",
    "Quick service and food courts",
    "Cafés and coffee shops",
    "Hotels and restaurant chains",
]

FUNCTION_TABS = [
    {"name": "Restaurant & Bar",
     "title": "Syrve for full-service restaurants and bars",
     "checks": ["Fast, easy POS for front-of-house teams",
                "Orders sent straight to the right kitchen or bar station",
                "Table plans, split bills and course timing",
                "Voids and discounts tracked by staff member"],
     "extras": ["Waiter app for ordering at the table",
                "Recipe-level stock control",
                "Menu performance reports"]},
    {"name": "Delivery",
     "title": "Syrve for delivery and takeaway",
     "checks": ["Website and aggregator orders in one POS",
                "Call-centre screen for phone orders",
                "Driver app with live order status",
                "Delivery zones and time estimates"],
     "extras": ["Route planning for drivers",
                "Customer order history",
                "Delivery performance reports"]},
    {"name": "Quick Service",
     "title": "Syrve for quick service and food courts",
     "checks": ["High-speed checkout for busy counters",
                "Self-order kiosks and QR menus",
                "Kitchen display screens instead of paper tickets",
                "Combo meals and modifiers"],
     "extras": ["Queue and order-ready screens",
                "Peak-hour sales forecasting",
                "Multi-outlet menu control"]},
    {"name": "Café",
     "title": "Syrve for cafés and coffee shops",
     "checks": ["Simple till that new staff learn in minutes",
                "Loyalty stamps and member discounts",
                "Stock alerts for milk, beans and bakery items",
                "Cash, card and split payments"],
     "extras": ["Online pre-orders for pick-up",
                "Daily cash and sales summary",
                "Cost of goods per drink"]},
]

ASSISTANTS = [
    "Kitchen display system (KDS) for chefs",
    "Manager dashboard with live sales and alerts",
    "Waiter app for taking orders at the table",
    "Driver app for fast, tracked deliveries",
]

LOYALTY = [
    "Points, cashback, discounts and promotions configured your way",
    "Happy-hour and time-based pricing",
    "Guest segments based on what and when they order",
    "Gift cards and vouchers you can issue and track",
    "SMS campaigns to bring guests back",
]

BACK_OFFICE = [
    "Purchasing, invoices and stock documents on any device",
    "Automatic supplier orders based on stock levels",
    "Staff scheduling, attendance and performance",
    "Cash flow, profit and loss and balance reports",
    "One place to manage every outlet in a chain",
]

PACKAGES = [
    {"name": "Café", "for": "For cafés, coffee shops and small kiosks",
     "tag": "Great for a single outlet", "tag_class": "rs-tag--yellow", "featured": False,
     "items": ["POS and sales management", "Simple stock control", "Daily sales reports"]},
    {"name": "Restaurant", "for": "For restaurants and bars with a full kitchen",
     "tag": "Most popular", "tag_class": "rs-tag--green", "featured": True,
     "items": ["Full stock and recipe costing", "Kitchen display and waiter app",
               "Syrve Loyalty for repeat guests"]},
    {"name": "Chain", "for": "For chains, delivery brands and hotels",
     "tag": "Multi-outlet and delivery", "tag_class": "rs-tag--blue", "featured": False,
     "items": ["Call centre and delivery management", "Central menu and reporting",
               "Integrations with your own systems"]},
]

SERVICES = [
    {"title": "Support and consulting",
     "text": "Our Nairobi team answers by phone, WhatsApp and on site. We fix issues fast and "
             "help you get more out of Syrve as your business grows."},
    {"title": "Installation and training",
     "text": "We set up Syrve around your menu and workflow, connect your printers and "
             "payment options, and train your staff until they are confident."},
    {"title": "POS hardware",
     "text": "Terminals, receipt printers, kitchen screens, cash drawers and networking from "
             "our own stock, installed and tested with Syrve."},
]

STEPS = [
    {"title": "Free consultation",
     "text": "We visit or call to understand your menu, service style, outlets and budget, "
             "then recommend the right Syrve set-up."},
    {"title": "Set-up and installation",
     "text": "We configure Syrve with your menu, prices, printers and staff roles, and "
             "install and test the hardware on site."},
    {"title": "Staff training",
     "text": "Waiters, cashiers, kitchen and managers each learn the screens they use, so "
             "you go live with confidence."},
    {"title": "Ongoing support",
     "text": "Our Nairobi team stays on call by phone, WhatsApp and on site as your business "
             "grows."},
]

FAQ = [
    {"q": "What is Syrve?",
     "a": "Syrve is an all-in-one POS and restaurant management software that helps food and "
          "beverage businesses increase performance and spend less time on routine "
          "administrative tasks."},
    {"q": "Who is the official Syrve distributor in Kenya and East Africa?",
     "a": "Jabem Solutions is the official Syrve distributor for East Africa. We handle sales, "
          "rollout, training and day-to-day support for Syrve in Kenya and across the region, "
          "with Syrve's own team behind us."},
    {"q": "Is Syrve available in Uganda, Tanzania and Rwanda?",
     "a": "Yes. As the official Syrve distributor for East Africa, Jabem Solutions supplies and "
          "supports Syrve for restaurants, hotels and chains in Uganda, Tanzania, Rwanda and "
          "the rest of East Africa, not just Kenya."},
    {"q": "Which businesses is Syrve for?",
     "a": "Restaurants, cafés and bakeries, quick-service restaurants, bars and pubs, hotels "
          "and hospitality businesses, and restaurant groups and chains."},
    {"q": "Does Syrve work with the tools we already use?",
     "a": "Syrve connects to delivery platforms, accounting software and payment providers "
          "through an open API, so the systems you already run keep working together with "
          "your POS."},
    {"q": "How much does Syrve cost?",
     "a": "Pricing depends on the number of outlets, terminals and modules you need. Leave "
          "your phone number or call +254 736 794 594 and we will send a quote for your "
          "business."},
    {"q": "Can you supply the hardware too?",
     "a": "Yes. Jabem Solutions supplies and installs POS terminals, receipt printers, kitchen "
          "screens, cash drawers and networking, all tested to work with Syrve."},
    {"q": "How can I see Syrve in action?",
     "a": "Leave your phone number in the form on this page, or call us on +254 736 794 594. "
          "We will show you what the system can do for your restaurant."},
]
