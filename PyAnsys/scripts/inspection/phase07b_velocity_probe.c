/* Phase7b diagnostic: copy guarded phase velocities to UDM0..2 for comparison
 * with native cell-centred ASCII phase fields. No physical-field mutations,
 * sources, initialization or solver iteration. Requires 6 UDM slots.
 * Slots3..5 hold mixture velocity. UDM values are numerical SI m/s.
 */
#include "udf.h"
#include <math.h>

DEFINE_ON_DEMAND(phase07b_velocity_probe)
{
#if !RP_HOST
    Domain *d=Get_Domain(1);
    Thread *t, *l;
    cell_t c;
    int ok=Data_Valid_P() ? 1:0, count=0, nonzero=0;
    real maxdrift=0, liquid_volume=0;
    if (n_udm<6) ok=0;
    if (ok) {
        thread_loop_c(t,d) {
            if (!FLUID_THREAD_P(t)) continue;
            if (NULLP(THREAD_SUB_THREADS(t))) {ok=0;continue;}
            l=THREAD_SUB_THREAD(t,1);
            if (NULLP(l) || NULLP(THREAD_STORAGE(l,SV_U)) ||
                NULLP(THREAD_STORAGE(l,SV_V)) || NULLP(THREAD_STORAGE(l,SV_W)) ||
                NULLP(THREAD_STORAGE(l,SV_VOF)) || NULLP(THREAD_STORAGE(t,SV_UDM_I))) ok=0;
        }
    }
#if RP_NODE
    ok=PRF_GILOW1(ok);
#endif
    if (!ok) {Message0("P7B_VELOCITY_PROBE unavailable_storage\n");return;}
    thread_loop_c(t,d) {
        if (!FLUID_THREAD_P(t)) continue;
        l=THREAD_SUB_THREAD(t,1);
        begin_c_loop_int(c,t) {
            real u[3]={C_U(c,l),C_V(c,l),C_W(c,l)};
            real m[3]={C_U(c,t),C_V(c,t),C_W(c,t)};
            real drift=0; int j;
            count++;
            for(j=0;j<3;j++) {
                C_UDMI(c,t,j)=u[j]; C_UDMI(c,t,j+3)=m[j];
                drift+=(u[j]-m[j])*(u[j]-m[j]);
            }
            drift=sqrt(drift);
            if(drift>1e-10) nonzero++;
            if(drift>maxdrift) maxdrift=drift;
            liquid_volume+=C_VOF(c,l)*C_VOLUME(c,t);
        } end_c_loop_int(c,t)
    }
#if RP_NODE
    count=PRF_GISUM1(count);nonzero=PRF_GISUM1(nonzero);
    maxdrift=PRF_GRHIGH1(maxdrift);liquid_volume=PRF_GRSUM1(liquid_volume);
#endif
    Message0("P7B_VELOCITY_PROBE cells=%d nonzero_drift_cells=%d max_drift=%.17g liquid_volume=%.17g iteration=%d\n",count,nonzero,maxdrift,liquid_volume,N_ITER);
#endif
}
