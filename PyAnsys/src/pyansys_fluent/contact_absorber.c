/* Phase 7.2A conservative liquid-only depletion in the existing collector.
 * Based on Fluent 2025 R2 DEFINE_SOURCE Example 2 (degassing).
 * Finite tau approximates perfect capture; never overwrite volume fraction.
 * Mass is hooked on phase-2; momentum on Mixture. No vapor mass source.
 * Rates are separate compiled functions to avoid unsynchronised RP state.
 */
#include "udf.h"

static real liquid_mass(cell_t c, Thread *liquid, real tau)
{
    return -C_R(c,liquid)*MAX(C_VOF(c,liquid),0.0)/tau;
}
static real mass_derivative(cell_t c, Thread *liquid, real tau, int eqn)
{
    /* Diagnostic provenance: verify which native equation requests the source.
     * The callback index is not publicly documented as the EQ_* enum.
     * Printed symbols are provenance only; do not branch derivatives on them.
     */
#if RP_NODE
    static int seen[256]={0};
    if (eqn>=0 && eqn<256 && !seen[eqn]) {
        seen[eqn]=1;
        Message0("CONTACT_MASS_CALLBACK eqn=%d EQ_VOF=%d EQ_CONTINUITY=%d tau=%g\n",
                 eqn,EQ_VOF,EQ_CONTINUITY,tau);
    }
#endif
    return -C_R(c,liquid)/tau;
}
static real mixture_momentum(cell_t c, Thread *mix, real *dS,
                             int eqn, real tau, int axis)
{
    Thread *liquid=THREAD_SUB_THREAD(mix,1);
    real mass=liquid_mass(c,liquid,tau);
    /* Remove the liquid's momentum; liquid and Mixture velocities differ.
     * Implicit derivative holds slip fixed during the Mixture update.
     */
    real velocity=axis==0 ? C_U(c,liquid) : (axis==1 ? C_V(c,liquid) : C_W(c,liquid));
    dS[eqn]=mass;
    return mass*velocity;
}
DEFINE_SOURCE(contact_mass_1ms,c,t,dS,eqn)
{dS[eqn]=mass_derivative(c,t,0.001,eqn); return liquid_mass(c,t,0.001);}
DEFINE_SOURCE(contact_x_1ms,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.001,0);}
DEFINE_SOURCE(contact_y_1ms,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.001,1);}
DEFINE_SOURCE(contact_z_1ms,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.001,2);}
DEFINE_SOURCE(contact_mass_100us,c,t,dS,eqn)
{dS[eqn]=mass_derivative(c,t,0.0001,eqn); return liquid_mass(c,t,0.0001);}
DEFINE_SOURCE(contact_x_100us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.0001,0);}
DEFINE_SOURCE(contact_y_100us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.0001,1);}
DEFINE_SOURCE(contact_z_100us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.0001,2);}
DEFINE_SOURCE(contact_mass_10us,c,t,dS,eqn)
{dS[eqn]=mass_derivative(c,t,0.00001,eqn); return liquid_mass(c,t,0.00001);}
DEFINE_SOURCE(contact_x_10us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.00001,0);}
DEFINE_SOURCE(contact_y_10us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.00001,1);}
DEFINE_SOURCE(contact_z_10us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.00001,2);}
DEFINE_SOURCE(contact_mass_1us,c,t,dS,eqn)
{dS[eqn]=mass_derivative(c,t,0.000001,eqn); return liquid_mass(c,t,0.000001);}
DEFINE_SOURCE(contact_x_1us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.000001,0);}
DEFINE_SOURCE(contact_y_1us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.000001,1);}
DEFINE_SOURCE(contact_z_1us,c,t,dS,eqn)
{return mixture_momentum(c,t,dS,eqn,0.000001,2);}
