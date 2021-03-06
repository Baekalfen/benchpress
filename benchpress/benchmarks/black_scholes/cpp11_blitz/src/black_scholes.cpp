#include <blitz/array.h>
#include <random/uniform.h>
#include <bp_util.h>

using namespace blitz;
using namespace ranlib;

template <typename T>
Array<T, 1> cnd(Array<T, 1> & x)
{
    int samples = x.numElements();
    Array<T, 1> l(samples), k(samples), w(samples), res(samples);
    Array<bool, 1> mask(samples);
    T a1 = 0.31938153,
      a2 =-0.356563782,
      a3 = 1.781477937,
      a4 =-1.821255978,
      a5 = 1.330274429,
      pp = 2.5066282746310002; // sqrt(2.0*PI)

    l = abs(x);
    k = 1.0 / (1.0 + 0.2316419 * l);
    w = 1.0 - 1.0 / pp * exp(-1.0*l*l/2.0) * \
        (a1*k + \
         a2*(pow(k,(T)2)) + \
         a3*(pow(k,(T)3)) + \
         a4*(pow(k,(T)4)) + \
         a5*(pow(k,(T)5)));

    mask    = x < 0.0;
    res     = (w * cast<T>(!mask) + (1.0-w)* cast<T>(mask));
    return res;
}

template <typename T>
T* pricing(size_t samples, size_t iterations, char flag, T x, T d_t, T r, T v)
{
    Array<T, 1> d1(samples), d2(samples), res(samples);
    T* p    = (T*)malloc(sizeof(T)*samples);    // Intermediate results
    T t     = d_t;                              // Initial delta

    Array<T, 1> s(samples);                     // Initial uniform sampling
    Uniform<T> rand;                            // values between 58-62
    rand.seed((unsigned int)time(0));
    s = rand.random() *4.0 +58.0;

    for(size_t i=0; i<iterations; i++) {
        d1 = (log(s/x) + (r+v*v/2.0)*t) / (v*sqrt(t));
        d2 = d1-v*sqrt(t);
        if (flag == 'c') {
            res = s * cnd(d1) - x * exp(-r * t) * cnd(d2);
        } else {
            Array<T, 1> tmp1(samples), tmp2(samples);
            tmp1 = -1.0*d2;
            tmp2 = -1.0*d1;

            res = x * exp(-r*t) * cnd(tmp1) - s*cnd(tmp2);
        }
        t += d_t;                               // Increment delta
        p[i] = sum(res) / (T)samples;           // Result from timestep
    }

    return p;
}

//FLOP count: 2*s+i*(s*8+2*s*23) where s is samples and i is iterations

int main(int argc, char* argv[])
{
    bp_util_type bp = bp_util_create(argc, argv, 2);
    if (bp.args.has_error) {
        return 1;
    }
    const size_t samples    = bp.args.sizes[0];
    const size_t iterations = bp.args.sizes[1];

    bp.timer_start();
    double* prices = pricing(
        samples, iterations,
        'c', 65.0, 1.0 / 365.0,
        0.08, 0.3
    );
    bp.timer_stop();
    
    bp.print("black_scholes(cpp11_blitz)");
    if (bp.args.verbose) {
        cout << ", \"output\": [";
        for(size_t i=0; i<iterations; i++) {
            cout << prices[i];
            if (iterations-1!=i) {
                cout << ", ";
            }
        }
        cout << "]" << endl;
    }

    free(prices);
    return 0;
}


