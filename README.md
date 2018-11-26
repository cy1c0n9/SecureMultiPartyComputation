Complete all part of the coursework

    Implemented all features required for garbled circuit construction and evaluation
    Implemented oblivious transfer protocol
    Implemented other code e.g. in main to make it runable
    JSON circuit for Millionaires in ./json/f.million.json

How to run the code:
    
    Typically use two different terminal, one for bob and one for alice
    run "make bob" for bob and
    run "make alice" or other test case like "make bool" for alice
    if you run "make bob" first, 
        you will get output looks like output_given in ./out.txt
    if you run "make alice" first,
        you will get almost same output except the first line
            "python3 main.py alice	 json/f.bool.json"
        is likely to be missing in ./out.txt
    
    In order to make output looks good, we use sleep function to delay the IO
    but it will not take too much time to run it.
 
For DEBUG
    
    The DEBUG button is in yao.py,
    simply change DEBUG = 1, run the code again,
    the detail will be showed on the terminal.
    if you change DEBUG = 2, run the code again,
    the extremely detail will be showed on the terminal
    
    
Garble Circuit parts files: yao.py crypto.py

    yao.py:
    super class:    Circuits Wire shared with alice and bob
    sub-class:      AliceCircuits Gate AliceWire used by alice
                    BobCircuits GarbleTable used by bob
    and some util functions
    
    crypto.py:      encryption and decryption function and some util functions

OT parts files : alice_ot.py bob_ot.py ot.py

    alice_ot.py:
    functions : Alice's terminal in OT.
                Alice inputs message0 and message1 and gets nothing from OT.

    bob_ot.py:
    functions : Bob's terminal in OT.
                Bob inputs a bit b to select a message and Bob gets a real message from OT.

    ot.py:
    Including two classes.
    class Alice : 
    functions : according to an IND-CPA version of DHIES and
                the optimization of smart,
                in Alice class, Alice encrypts messages.

    class Bob:
    functions : according to an IND-CPA version of DHIES and
                the optimization of smart, 
                in Bob class, 
                Bob double-encrypts pairs of messages and
                then decrypts messages.
                
Other code:

    Alice.py:   
    class Alice:    everything alice should do to generate truth table like output_given
    
    Bob.py:  
    class bob:      everything bob should do