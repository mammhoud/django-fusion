// @generated automatically by Diesel CLI.
// Hand-edited to match the initial migration schema.

diesel::table! {
    settings (id) {
        id -> Integer,
        restaurant_name -> Nullable<Text>,
        address -> Nullable<Text>,
        phone -> Nullable<Text>,
        email -> Nullable<Text>,
        tax_rate -> Nullable<Text>,
        tax_id -> Nullable<Text>,
        currency -> Text,
        opening_time -> Nullable<Text>,
        closing_time -> Nullable<Text>,
        receipt_footer -> Nullable<Text>,
        logo -> Nullable<Text>,
        invoice_logo -> Nullable<Text>,
        dine_in_tables -> Integer,
        delivery_fee -> Double,
        delivery_fee_per_km -> Double,
        smtp_server -> Nullable<Text>,
        smtp_port -> Nullable<Integer>,
        smtp_username -> Nullable<Text>,
        smtp_password -> Nullable<Text>,
        smtp_recipient -> Nullable<Text>,
        smtp_from_name -> Nullable<Text>,
        smtp_from_email -> Nullable<Text>,
    }
}

diesel::table! {
    categories (id) {
        id -> Integer,
        name -> Text,
        color -> Nullable<Text>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    products (id) {
        id -> Integer,
        name -> Text,
        price -> Double,
        unit -> Text,
        category_id -> Nullable<Integer>,
        image -> Nullable<Text>,
        product_type -> Text,
        prepare_time_minutes -> Integer,
        barcode -> Nullable<Text>,
        description -> Nullable<Text>,
        available_order_types -> Text,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        uploaded -> Bool,
    }
}

diesel::table! {
    delivery_types (id) {
        id -> Integer,
        name -> Text,
        description -> Nullable<Text>,
        fee_multiplier -> Double,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    employee_types (id) {
        id -> Integer,
        name -> Text,
        description -> Nullable<Text>,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    employees (id) {
        id -> Integer,
        name -> Text,
        phone -> Nullable<Text>,
        email -> Nullable<Text>,
        employee_type_id -> Integer,
        salary -> Double,
        is_active -> Bool,
        joined_at -> Nullable<Text>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        uploaded -> Bool,
        address -> Nullable<Text>,
        date_of_birth -> Nullable<Text>,
        national_id -> Nullable<Text>,
        emergency_contact -> Nullable<Text>,
        pay_frequency -> Text,
        hourly_rate -> Double,
        bank_name -> Nullable<Text>,
        bank_account -> Nullable<Text>,
        tax_number -> Nullable<Text>,
        notes -> Nullable<Text>,
    }
}

diesel::table! {
    sales (id) {
        id -> Integer,
        total_amount -> Double,
        currency -> Text,
        date -> Text,
        time -> Text,
        order_type -> Text,
        status -> Text,
        table_number -> Nullable<Integer>,
        delivery_type_id -> Nullable<Integer>,
        delivery_zone_id -> Nullable<Integer>,
        delivery_address -> Nullable<Text>,
        employee_id -> Nullable<Integer>,
        customer_id -> Nullable<Integer>,
        discount_code -> Nullable<Text>,
        discount_amount -> Double,
        payment_method -> Text,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        uploaded -> Bool,
    }
}

diesel::table! {
    coupons (id) {
        id -> Integer,
        code -> Text,
        kind -> Text,
        value -> Double,
        min_subtotal -> Nullable<Double>,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    user_actions (id) {
        id -> Integer,
        action -> Text,
        entity_type -> Nullable<Text>,
        entity_id -> Nullable<Integer>,
        details -> Nullable<Text>,
        user_id -> Nullable<Integer>,
        created_at -> Timestamp,
    }
}

diesel::table! {
    sale_items (id) {
        id -> Integer,
        sale_id -> Integer,
        product_name -> Text,
        price -> Double,
        quantity -> Double,
        unit -> Text,
        subtotal -> Double,
        created_at -> Timestamp,
    }
}

diesel::table! {
    ingredients (id) {
        id -> Integer,
        name -> Text,
        unit -> Text,
        current_quantity -> Double,
        reorder_level -> Double,
        reorder_quantity -> Double,
        cost_per_unit -> Double,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        uploaded -> Bool,
    }
}

diesel::table! {
    recipe_types (id) {
        id -> Integer,
        name -> Text,
        description -> Nullable<Text>,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    recipes (id) {
        id -> Integer,
        product_id -> Integer,
        recipe_type_id -> Integer,
        yield_quantity -> Double,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        uploaded -> Bool,
    }
}

diesel::table! {
    recipe_ingredients (id) {
        id -> Integer,
        recipe_id -> Integer,
        ingredient_id -> Integer,
        quantity -> Double,
        unit -> Nullable<Text>,
        preparation_note -> Nullable<Text>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    inventory_transactions (id) {
        id -> Integer,
        ingredient_id -> Integer,
        transaction_type -> Text,
        quantity_change -> Double,
        reference_id -> Nullable<Integer>,
        note -> Nullable<Text>,
        created_at -> Timestamp,
        uploaded -> Bool,
    }
}

diesel::table! {
    inventory_adjustments (id) {
        id -> Integer,
        ingredient_id -> Integer,
        previous_quantity -> Double,
        new_quantity -> Double,
        reason -> Text,
        created_by -> Nullable<Text>,
        created_at -> Timestamp,
        uploaded -> Bool,
    }
}

diesel::joinable!(employees -> employee_types (employee_type_id));
diesel::joinable!(products -> categories (category_id));
diesel::joinable!(sales -> delivery_types (delivery_type_id));
diesel::joinable!(sales -> employees (employee_id));
diesel::joinable!(recipes -> products (product_id));
diesel::joinable!(recipes -> recipe_types (recipe_type_id));
diesel::joinable!(recipe_ingredients -> recipes (recipe_id));
diesel::joinable!(recipe_ingredients -> ingredients (ingredient_id));
diesel::joinable!(inventory_transactions -> ingredients (ingredient_id));
diesel::joinable!(inventory_adjustments -> ingredients (ingredient_id));

diesel::table! {
    users (id) {
        id -> Integer,
        email -> Text,
        password_hash -> Text,
        name -> Text,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    roles (id) {
        id -> Integer,
        name -> Text,
        permissions -> Text,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    user_roles (user_id, role_id) {
        user_id -> Integer,
        role_id -> Integer,
        created_at -> Timestamp,
    }
}

diesel::table! {
    report_metadata (id) {
        id -> Integer,
        report_type -> Text,
        format -> Text,
        file_path -> Text,
        parameters -> Nullable<Text>,
        generated_by -> Nullable<Integer>,
        created_at -> Timestamp,
    }
}

diesel::table! {
    inventory_alerts (id) {
        id -> Integer,
        ingredient_id -> Integer,
        alert_type -> Text,
        alert_message -> Text,
        is_resolved -> Bool,
        created_at -> Timestamp,
        resolved_at -> Nullable<Timestamp>,
    }
}

diesel::table! {
    suppliers (id) {
        id -> Integer,
        name -> Text,
        contact_name -> Nullable<Text>,
        email -> Nullable<Text>,
        phone -> Nullable<Text>,
        address -> Nullable<Text>,
        tax_id -> Nullable<Text>,
        payment_terms -> Nullable<Text>,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    purchase_orders (id) {
        id -> Integer,
        supplier_id -> Integer,
        reference_number -> Nullable<Text>,
        status -> Text,
        total_amount -> Double,
        shipping_fee -> Double,
        expected_date -> Nullable<Timestamp>,
        notes -> Nullable<Text>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    purchase_order_items (id) {
        id -> Integer,
        purchase_order_id -> Integer,
        ingredient_id -> Integer,
        quantity -> Double,
        cost_per_unit -> Double,
        received_quantity -> Double,
    }
}

diesel::table! {
    kitchen_tickets (id) {
        id -> Integer,
        sale_id -> Integer,
        status -> Text,
        priority -> Integer,
        prepare_time_minutes -> Integer,
        notes -> Nullable<Text>,
        created_at -> Timestamp,
        completed_at -> Nullable<Timestamp>,
    }
}

diesel::table! {
    customers (id) {
        id -> Integer,
        name -> Text,
        phone -> Nullable<Text>,
        email -> Nullable<Text>,
        loyalty_points -> Double,
        notes -> Nullable<Text>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    loyalty_transactions (id) {
        id -> Integer,
        customer_id -> Integer,
        sale_id -> Nullable<Integer>,
        points_change -> Double,
        reason -> Text,
        created_at -> Timestamp,
    }
}

diesel::table! {
    receipt_templates (id) {
        id -> Integer,
        name -> Text,
        template_body -> Text,
        category -> Nullable<Text>,
        recipe_id -> Nullable<Integer>,
        is_default -> Bool,
        use_as_template -> Bool,
        selectable -> Bool,
        steps -> Nullable<Text>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    support_messages (id) {
        id -> Integer,
        name -> Text,
        email -> Text,
        phone -> Nullable<Text>,
        subject -> Nullable<Text>,
        category -> Nullable<Text>,
        priority -> Text,
        message -> Text,
        status -> Text,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    tax_reports (id) {
        id -> Integer,
        period_start -> Text,
        period_end -> Text,
        total_sales -> Double,
        total_tax -> Double,
        transaction_count -> Integer,
        generated_at -> Timestamp,
    }
}

diesel::table! {
    employee_schedules (id) {
        id -> Integer,
        employee_id -> Integer,
        shift_start -> Timestamp,
        shift_end -> Timestamp,
        status -> Text,
        notes -> Nullable<Text>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    payrolls (id) {
        id -> Integer,
        employee_id -> Integer,
        period_start -> Text,
        period_end -> Text,
        regular_hours -> Double,
        overtime_hours -> Double,
        total_pay -> Double,
        status -> Text,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::table! {
    delivery_zones (id) {
        id -> Integer,
        name -> Text,
        base_fee -> Double,
        fee_per_km -> Double,
        max_distance -> Double,
        is_active -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

diesel::joinable!(user_roles -> users (user_id));
diesel::joinable!(user_roles -> roles (role_id));
diesel::joinable!(report_metadata -> users (generated_by));
diesel::joinable!(inventory_alerts -> ingredients (ingredient_id));
diesel::joinable!(purchase_orders -> suppliers (supplier_id));
diesel::joinable!(purchase_order_items -> purchase_orders (purchase_order_id));
diesel::joinable!(purchase_order_items -> ingredients (ingredient_id));
diesel::joinable!(kitchen_tickets -> sales (sale_id));
diesel::joinable!(loyalty_transactions -> customers (customer_id));
diesel::joinable!(loyalty_transactions -> sales (sale_id));
diesel::joinable!(employee_schedules -> employees (employee_id));
diesel::joinable!(payrolls -> employees (employee_id));

diesel::allow_tables_to_appear_in_same_query!(
    users,
    roles,
    user_roles,
    settings,
    categories,
    products,
    delivery_types,
    employee_types,
    employees,
    sales,
    sale_items,
    ingredients,
    recipe_types,
    recipes,
    recipe_ingredients,
    inventory_transactions,
    inventory_adjustments,
    report_metadata,
    inventory_alerts,
    suppliers,
    purchase_orders,
    purchase_order_items,
    kitchen_tickets,
    customers,
    loyalty_transactions,
    receipt_templates,
    tax_reports,
    employee_schedules,
    payrolls,
    delivery_zones,
    support_messages,
    coupons,
    user_actions,
);
