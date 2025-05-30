from .db import conn, cursor

def initialize_database():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS User (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        nickname VARCHAR(50),
        gender ENUM('male','female'),
        contact VARCHAR(20),               
        real_name VARCHAR(100),
        phone_number VARCHAR(20),
        profile_image VARCHAR(255),
        user_type ENUM('normal', 'admin') DEFAULT 'normal',
        trust_score INT DEFAULT 0,
        activity_score INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login_at DATETIME,
        is_active BOOLEAN DEFAULT TRUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Restaurant (
        restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        address VARCHAR(255) NOT NULL,
        category VARCHAR(50),
        phone VARCHAR(20),
        latitude DECIMAL(10, 7),
        longitude DECIMAL(10, 7),
        average_rating FLOAT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tag (
        tag_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS RestaurantTag (
        restaurant_id INT,
        tag_id INT,
        PRIMARY KEY (restaurant_id, tag_id),
        FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES Tag(tag_id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Review (
        review_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        restaurant_id INT,
        rating INT,
        content TEXT,
        image_url VARCHAR(255),
        receipt_verified BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
        FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ReviewDetail (
        review_id INT PRIMARY KEY,
        taste_rating TINYINT,
        price_rating TINYINT,
        service_rating TINYINT,
        FOREIGN KEY (review_id) REFERENCES Review(review_id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ReviewImage (
        review_image_id INT AUTO_INCREMENT PRIMARY KEY,
        review_id INT,
        image_url VARCHAR(255),
        FOREIGN KEY (review_id) REFERENCES Review(review_id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS `Like` (
        user_id INT,
        review_id INT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, review_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
        FOREIGN KEY (review_id) REFERENCES Review(review_id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserScore (
        user_id INT PRIMARY KEY,
        review_count INT DEFAULT 0,
        like_received_count INT DEFAULT 0,
        receipt_verified_count INT DEFAULT 0,
        trust_score INT DEFAULT 0,
        activity_score INT DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS LoginHistory (
        login_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        logout_time DATETIME,
        ip_address VARCHAR(45),
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Terms (
        terms_id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        content TEXT NOT NULL,
        is_required BOOLEAN DEFAULT TRUE,
        version VARCHAR(20),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserAgreement (
        agreement_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        terms_id INT NOT NULL,
        agreed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
        FOREIGN KEY (terms_id) REFERENCES Terms(terms_id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    print("DB 초기화 완료!")