
import customtkinter as ctk
root = ctk.CTk()
root.withdraw()
entry = ctk.CTkEntry(root)
entry.pack()

def handler(event=None):
    raw = (entry.get() or '').strip()
    print('handler called raw', repr(raw))
    digits = ''.join(ch for ch in raw if ch.isdigit())
    digits = digits[:5]
    if digits != raw:
        entry.delete(0, 'end')
        entry.insert(0, digits)
    print('handler after', repr(entry.get()))

entry.bind('<KeyRelease>', handler)

# Simulate typing
for ch in '12345':
    entry.insert('end', ch)
    handler()
    print('after type', entry.get())

print('final', entry.get())
root.destroy()
