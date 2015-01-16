Benchmark
#########


Result
======

ab  -n10000 -c500   http://localhost:8080/

Run in
Python 2.7.9
Intel(R) Core(TM) i7-3520M CPU @ 2.90GHz
8GB RAM

.. table:: 
    
   
    ============== ============ =========== ========== ============== 
    app            server       workers     requets    request/sec  
    ============== ============ =========== ========== ============== 
    bottle         gevent         500        10000     3623.53
    falcon         gevent         500        10000     4686.68
    tornado        tornado        500        10000     1315.57   
    flask          gevent         500        10000     2594.68
    django         gevent         500        10000     2668.52
    solo           gevent         500        10000     3532.94
    ============== ============ =========== ========== ============== 

