build a highly efficient and user-friendly web-based system for a rural LPG dealer named Vios Prycegas Tambulig Station. The goal is to transition their current manual order tracking and inventory process to a digital-first platform that works seamlessly on both desktop and mobile. You must use the following tech stack : 

Backend: Django

Frontend: TailwindCSS + HTMX + Alpine.js + Unpoly

Database: SQLite (local development) 

🎯 Project Overview:
Name: Web-Based Prycegas Dealer and Distributor Information System
Users:

Customers: Can register, log in, place LPG orders online, and view delivery status.

Dealer/Admin: Manages orders, tracks inventory, logs batch deliveries from distributor, and generates sales and stock reports.

📐 Functional Specifications:
1. Customer Module
Register / Login (user authentication via Django’s built-in auth)

Submit LPG orders (select quantity, delivery type: pickup/delivery)

View order history and real-time status (HTMX for dynamic updates)

Mobile-first responsive design (TailwindCSS + Alpine.js interactivity)

2. Dealer/Admin Module
Dashboard (Unpoly-enhanced for snappy updates without full reload) The dashboard is sidebar that can toggle and collapsible for mobile view 

Order Management:

View all customer orders (sortable, filterable)

Update status: Pending → Out for Delivery → Delivered

Inventory Management:

View current stock levels

Log distributor deliveries (DeliveryLog class)

Auto-adjust inventory when orders are made or stock is received

Report Generation (HTML reports for now; exportable in future)

Notifications (in-system using Alpine.js for alerts/toasts)

🧩 Technical Requirements:
Django views must support HTMX and Unpoly for fast partial updates.

Use Alpine.js for modal confirmations, dynamic form interactions, and toggling UI states.

Use TailwindCSS classes throughout for utility-first, responsive design.

REST endpoints can be minimized since most interaction is server-rendered and enhanced with HTMX/Unpoly.

SQLite used for development, abstract models for portability to PostgreSQL.

No JS frameworks like React or Vue—favor progressive enhancement.

🔒 Non-Functional Specifications:
Usability: Even non-tech-savvy users must find the interface intuitive.

Performance: Optimized for rural areas with slow internet.

Maintainability: Codebase should be modular, readable, and Django admin-friendly.

Accessibility: Interface readable on both low-end smartphones and desktops.

Security: CSRF protection, authenticated routes, safe form validations.

🔌 UX Behavior via HTMX & Unpoly:
Action	Tech Used	Behavior
Order form submission	HTMX	Inline form validation, auto-update order list on submit
Inventory update	Unpoly	Dealer sees updated stock without page refresh
Modal delivery logs	Alpine.js	Dealer logs new delivery via modal with form reset on success
Toast notifications	Alpine.js	Auto-dismiss alerts for order success/error messages
