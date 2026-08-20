import sqlite3

def run_migration():
    conn = sqlite3.connect('database/evi_center.db')
    cursor = conn.cursor()
    
    # Check if current_lesson_num exists in class_schedule_adjustments
    cursor.execute("PRAGMA table_info(class_schedule_adjustments)")
    cols = [c[1] for c in cursor.fetchall()]
    print("Existing columns:", cols)
    
    if 'current_lesson_num' not in cols:
        print("Adding column current_lesson_num to class_schedule_adjustments...")
        cursor.execute("ALTER TABLE class_schedule_adjustments ADD COLUMN current_lesson_num INTEGER")
        conn.commit()
        print("Column added successfully!")
    else:
        print("Column current_lesson_num already exists.")
        
    conn.close()

if __name__ == '__main__':
    run_migration()
