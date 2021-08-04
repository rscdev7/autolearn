"""
@author           	    :  rscalia                              \n
@build-date             :  Wed 04/07/2021                       \n
@last-update            :  Wed 04/07/2021                       \n

Questo componente serve per testare la classe StreamingPipe
"""


from .Step_1       import Step_1
from .Step_2       import Step_2
from .Step_3       import Step_3


def test_streaming_pipeline_positive():
    print ("\nTEST POSITIVE \n")
    ls          = [ 0 , 1, 2, 3, 4 ]
    iterator    = iter ( ls )
    exception   = False

    pipe_1      = Step_1(iterator)
    pipe_2      = Step_1()
    pipe_3      = Step_1()
    pipe_4      = Step_1()
    outcome     = pipe_1 | pipe_2 | pipe_3
    

    try:
        for out in outcome:
            print(out)

    except Exception as exp:
        exception = True
    
    
    assert exception == False


def test_streaming_pipeline_negative():
    print ("TEST NEGATIVE \n")
    ls          = [ 80,100,200,300 ]
    iterator    = iter ( ls )
    exception   = False

    pipe_1      = Step_1(iterator)
    pipe_2      = Step_1()
    pipe_3      = Step_1()
    pipe_4      = Step_1()
    outcome     = pipe_1 | pipe_2 | pipe_3
    

    try:
        for _ in outcome:
            continue

    except Exception as exp:
        exception = True
    

    assert exception == True


def test_streaming_pipeline_one():
    print ("TEST ONE \n")
    ls          = [ 8 ]
    iterator    = iter ( ls )
    exception   = False

    pipe_1      = Step_1(iterator)
    pipe_2      = Step_1()
    pipe_3      = Step_1()
    pipe_4      = Step_1()
    outcome     = pipe_1 | pipe_2 | pipe_3
    

    try:
        el = next(outcome)
        print(el)
    except Exception as exp:
        exception = True
    

    assert exception == False


def test_streaming_pipeline_one_step_2():
    print ("TEST ONE STEP 2\n")
    exception   = False

    pipe_1      = Step_2()
    pipe_2      = Step_2()
    pipe_3      = Step_3()
    outcome     = pipe_1 | pipe_2 | pipe_3
    
    try:
        el = next(outcome)
        print(el)
    except Exception as exp:
        exception = True
    

    assert exception == False