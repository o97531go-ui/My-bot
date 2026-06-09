import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """إدارة قاعدة البيانات"""
    
    def __init__(self, db_path: str = "bot_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_interaction TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                is_premium BOOLEAN DEFAULT 0,
                is_blocked BOOLEAN DEFAULT 0,
                language TEXT DEFAULT 'ar'
            )
        ''')
        
        # جدول المحادثات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_text TEXT,
                response_text TEXT,
                conversation_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول الملفات المحللة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyzed_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_name TEXT,
                file_summary TEXT,
                pages_count INTEGER,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول الأسئلة المولدة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_text TEXT,
                answer_text TEXT,
                subject TEXT,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_answered BOOLEAN DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول المفضلة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content_type TEXT,
                content_id INTEGER,
                content_text TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول الإحصائيات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pdf_analyzed_count INTEGER DEFAULT 0,
                questions_generated INTEGER DEFAULT 0,
                conversations_count INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول الرسائل الترويجية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promotional_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_title TEXT,
                message_content TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول التنبيهات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notification_text TEXT,
                notification_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ تم إنشاء جداول قاعدة البيانات")
    
    # --- إدارة المستخدمين ---
    
    def add_user(self, user_id: int, first_name: str, last_name: str = "", username: str = "") -> bool:
        """إضافة مستخدم جديد"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, first_name, last_name, username, last_interaction)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, first_name, last_name, username, datetime.now()))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ تم إضافة مستخدم: {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في إضافة مستخدم: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """الحصول على بيانات المستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            return dict(user) if user else None
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على المستخدم: {e}")
            return None
    
    def update_user_interaction(self, user_id: int) -> bool:
        """تحديث آخر تفاعل للمستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET last_interaction = ?, message_count = message_count + 1
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث التفاعل: {e}")
            return False
    
    # --- إدارة المحادثات ---
    
    def save_conversation(self, user_id: int, message: str, response: str, conv_type: str = "chat") -> bool:
        """حفظ محادثة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations 
                (user_id, message_text, response_text, conversation_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, message, response, conv_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ المحادثة: {e}")
            return False
    
    def get_user_conversations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """الحصول على محادثات المستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            conversations = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return conversations
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على المحادثات: {e}")
            return []
    
    # --- إدارة الملفات المحللة ---
    
    def save_analyzed_file(self, user_id: int, file_name: str, summary: str, pages_count: int) -> bool:
        """حفظ ملف محلل"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analyzed_files 
                (user_id, file_name, file_summary, pages_count)
                VALUES (?, ?, ?, ?)
            ''', (user_id, file_name, summary, pages_count))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ الملف المحلل: {e}")
            return False
    
    def get_user_analyzed_files(self, user_id: int, limit: int = 10) -> List[Dict]:
        """الحصول على الملفات المحللة للمستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM analyzed_files 
                WHERE user_id = ?
                ORDER BY analyzed_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            files = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return files
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الملفات: {e}")
            return []
    
    # --- إدارة الأسئلة ---
    
    def save_quiz_question(self, user_id: int, question: str, answer: str, subject: str = "عام") -> bool:
        """حفظ سؤال امتحان"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO quiz_questions 
                (user_id, question_text, answer_text, subject)
                VALUES (?, ?, ?, ?)
            ''', (user_id, question, answer, subject))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ السؤال: {e}")
            return False
    
    def get_user_quiz_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """الحصول على تاريخ الأسئلة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM quiz_questions 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            questions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return questions
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الأسئلة: {e}")
            return []
    
    # --- إدارة المفضلة ---
    
    def save_favorite(self, user_id: int, content_type: str, content_text: str) -> bool:
        """حفظ في المفضلة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO favorites 
                (user_id, content_type, content_text)
                VALUES (?, ?, ?)
            ''', (user_id, content_type, content_text))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ المفضلة: {e}")
            return False
    
    def get_user_favorites(self, user_id: int) -> List[Dict]:
        """الحصول على المفضلة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM favorites 
                WHERE user_id = ?
                ORDER BY saved_at DESC
            ''', (user_id,))
            
            favorites = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return favorites
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على المفضلة: {e}")
            return []
    
    # --- الإحصائيات ---
    
    def get_user_statistics(self, user_id: int) -> Optional[Dict]:
        """الحصول على إحصائيات المستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM statistics WHERE user_id = ?', (user_id,))
            stats = cursor.fetchone()
            conn.close()
            
            return dict(stats) if stats else None
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الإحصائيات: {e}")
            return None
    
    def create_user_statistics(self, user_id: int) -> bool:
        """إنشاء سجل إحصائيات للمستخدم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO statistics 
                (user_id) VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء الإحصائيات: {e}")
            return False
    
    def increment_pdf_count(self, user_id: int) -> bool:
        """زيادة عدد ملفات PDF المحللة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE statistics 
                SET pdf_analyzed_count = pdf_analyzed_count + 1,
                    last_updated = ?
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث إحصائيات PDF: {e}")
            return False
    
    def increment_quiz_count(self, user_id: int) -> bool:
        """زيادة عدد الأسئلة المولدة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE statistics 
                SET questions_generated = questions_generated + 1,
                    last_updated = ?
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث إحصائيات الأسئلة: {e}")
            return False
    
    # --- الرسائل الترويجية والتنبيهات ---
    
    def send_promotional_message(self, user_id: int, title: str, content: str) -> bool:
        """إرسال رسالة ترويجية"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO promotional_messages 
                (user_id, message_title, message_content)
                VALUES (?, ?, ?)
            ''', (user_id, title, content))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال رسالة ترويجية: {e}")
            return False
    
    def get_user_promotions(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """الحصول على الرسائل الترويجية"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if unread_only:
                cursor.execute('''
                    SELECT * FROM promotional_messages 
                    WHERE user_id = ? AND is_read = 0
                    ORDER BY sent_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT * FROM promotional_messages 
                    WHERE user_id = ?
                    ORDER BY sent_at DESC
                ''', (user_id,))
            
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return messages
        except Exception as e:
            logger.error(f"❌ خطأ في الحصول على الرسائل الترويجية: {e}")
            return []
    
    def mark_promotion_as_read(self, message_id: int) -> bool:
        """وضع علامة على الرسالة الترويجية كمقروءة"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE promotional_messages 
                SET is_read = 1
                WHERE id = ?
            ''', (message_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في وضع علامة المقروء: {e}")
            return False
    
    def send_notification(self, user_id: int, text: str, notif_type: str = "info") -> bool:
        """إرسال تنبيه"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications 
                (user_id, notification_text, notification_type)
                VALUES (?, ?, ?)
            ''', (user_id, text, notif_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال التنبيه: {e}")
            return False
    
    # --- إحصائيات عامة ---
    
    def get_total_users(self) -> int:
        """عدد المستخدمين الكلي"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM users')
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ خطأ في حساب المستخدمين: {e}")
            return 0
    
    def get_active_users_today(self) -> int:
        """المستخدمون النشطون اليوم"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM users 
                WHERE DATE(last_interaction) = DATE('now')
            ''')
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ خطأ في حساب المستخدمين النشطين: {e}")
            return 0
