import log_processor
import json



notedic = {"NOTE": "THIS WAS ADDED MANUALLY. SERVER WAS DOWN FOR A FEW HOURS."}
note = json.dumps(notedic)
print ('SESSION ENDED')
stop = log_processor.write_event_to_db(log_processor.rightnow(), "SESSION ENDED", "imebneali", True, note)
print("stop:    "+ str(stop))
start = log_processor.get_pair_start_id("imebneali", "SESSION STARTED")
print("start:   "+ str(start))
if (start != -1):
    log_processor.add_pairid_to_db(start, stop)
log_processor.delete_all_pending_from_db("imebneali")