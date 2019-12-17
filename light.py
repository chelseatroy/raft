#Initial state of traffic light
Init = {
    'out1': 'G',
    'out2': 'R',
    'clock': 0,
    'button': False,
    'pc': 'G1'
}

# Define functions that determine state membership and state update.
# How to incorporate the button press?
G1 = lambda s: s['pc'] == 'G1' and (
    (s['clock'] < 30 and dict(s, clock=s['clock'] + 1))
    or (s['clock'] == 30 and dict(s, out1="Y", clock=0, pc="Y1"))
)

Y1 = lambda s: s['pc'] == 'Y1' and (
    (s['clock'] < 5 and dict(s, clock=s['clock'] + 1))
    or (s['clock'] == 5 and dict(s, out1='R', out2='G', clock=0, pc='G2'))
)

G2 = lambda s: s['pc'] == 'G2' and (
    ((s['clock'] == 60 or (s['clock'] >= 30 and s['button']))
     and dict(s, out2="Y", clock=0, button=False, pc="Y2"))
    or (s['clock'] < 60 and dict(s, clock=s['clock'] + 1))
)

Y2 = lambda s: s['pc'] == 'Y2' and (
    (s['clock'] < 5 and dict(s, clock=s['clock'] + 1))
    or (s['clock'] == 5 and dict(s, out1='G', out2='R', clock=0, pc='G1'))
)

# Next state relationship
Next = lambda s: G1(s) or Y1(s) or G2(s) or Y2(s)

def run():
    s = Init
    while s:
        print(s)
        s = Next(s)  # State transition


# If here. There was no next state
print("DEADLOCK")

run()