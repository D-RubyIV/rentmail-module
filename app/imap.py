import email
import imaplib
import logging
from datetime import datetime
from email.header import decode_header
from email.message import Message
from typing import List

from app.schemas import EmailMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImapBox:
    def __init__(self, email_string, secret_string):
        self.email_string = email_string
        self.secret_string = secret_string

    @staticmethod
    def get_body(msg: Message) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        return part.get_payload(decode=True).decode(
                            part.get_content_charset() or "utf-8",
                            errors="ignore"
                        )
                    except Exception as e:
                        logger.error(f"Lỗi khi giải mã nội dung: {e}")
                        return f"(Lỗi giải mã nội dung: {e})"
        else:
            try:
                return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")
            except Exception as e:
                logger.error(f"Lỗi khi giải mã nội dung: {e}")
                return f"(Lỗi giải mã nội dung: {e})"
        return "(Không tìm thấy nội dung phù hợp)"

    def print_hi(self) -> List[EmailMessage]:
        list_message: List[EmailMessage] = []
        imap = None
        try:
            logger.info("Bắt đầu kết nối đến Gmail IMAP")
            imap = imaplib.IMAP4_SSL("imap.gmail.com", timeout=30)
            imap.login(self.email_string, self.secret_string.replace(" ", ""))
            logger.info("Đăng nhập thành công")

            imap.select("INBOX")
            logger.info("Đã chọn INBOX")

            status, messages = imap.search(None, 'ALL')
            email_ids = messages[0].split()
            latest_5_ids = email_ids[-5:]
            logger.info(f"Tìm thấy {len(latest_5_ids)} email gần nhất")

            for eid in reversed(latest_5_ids):
                logger.info(f"Đang đọc email ID: {eid}")
                status, msg_data = imap.fetch(eid, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")

                from_ = msg.get("From")
                date_ = msg.get("Date")
                body_ = self.get_body(msg)

                message = EmailMessage(
                    subject=subject,
                    sender=from_,
                    date=datetime.now(),
                    body=body_,
                    messages=[]
                )
                list_message.append(message)
                logger.info(f"Đã đọc xong email: {subject}")

            logger.info("Hoàn thành việc đọc email")
            return list_message
        except Exception as e:
            logger.error(f"Lỗi khi đọc email: {str(e)}")
            raise Exception(f"Lỗi khi đọc email: {str(e)}")
        finally:
            if imap:
                try:
                    imap.logout()
                    logger.info("Đã đóng kết nối IMAP")
                except:
                    pass
