from pony.orm import *

db = Database();
def init_db():
	db.bind('sqlite', './data/db.db', create_db=True);
	db.generate_mapping(create_tables=True);

class WechatMsg(db.Entity):
	msg_id = Required(str);
	msg_time = Required(str);
	msg_time_rec = Required(str);
	msg_from = Required(str);
	msg_to = Required(str);
	msg_type = Required(str);
	msg = Optional(str);
	url = Optional(str);

@db_session
def select_all():
	ae = select(e for e in WechatMsg).order_by(desc(WechatMsg.id))[:];
	return ae;

@db_session
def select_id(id):
	rnt = select(e for e in WechatMsg if e.msg_id == id)
	if(len(rnt) <= 0):
		return None;
	return rnt[:][0];

@db_session
def db_insert(msg_id, msg_time, msg_time_rec, msg_from, msg_to, msg_type, msg, url):
	db.insert("WechatMsg",
		msg_id = msg_id,
		msg_time = msg_time,
		msg_time_rec = msg_time_rec,
		msg_from = msg_from,
		msg_to = msg_to,
		msg_type = msg_type,
		msg = msg,
		url = url);

@db_session
def db_insert(msg):
	db.insert("WechatMsg",
		msg_id = msg["msg_id"],
		msg_time = msg["msg_time"],
		msg_time_rec = msg["msg_time_rec"],
		msg_from = msg["msg_from"],
		msg_to = msg["msg_to"],
		msg_type = msg["msg_type"],
		msg = msg["msg"],
		url = msg["url"]);

def close_db():
	db.commit();
	db.disconnect();


# init_db();

