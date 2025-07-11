def add_message_to_history(history, role, message):
    """Επιστρέφει νέο history με το πρόσθετο μήνυμα"""
    new_entry = {"role": role, "content": message}
    return history + [new_entry]

def get_last_message(history):
    """Επιστρέφει το τελευταίο μήνυμα (ή None)"""
    return history[-1] if history else None

def clear_history():
    """Επιστρέφει κενό history"""
    return []

def get_chat_history(history):
    """Επιστρέφει όλο το history (αντιγραφή)"""
    return list(history)

def history_collector(history, role="assistant"):
    """Επιστρέφει μια συνάρτηση που προσθέτει chunks στο history_list"""    
    buffer = []

    def collect(chunk):
        buffer.append(chunk)
        return history  # δεν αλλάζουμε το history ακόμη

    def finalize():
        full_message = "".join(buffer)
        return add_message_to_history(history, role, full_message)

    return collect, finalize
