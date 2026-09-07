/*
 * Setup 07b: constant-water-level liquid sink for the split-inlet separator.
 *
 * Physical interpretation
 * -----------------------
 * The Fluent boundary named "bottom" is the assumed constant water-level
 * cutoff.  It remains an impermeable wall.  Liquid in the cells immediately
 * adjacent to that wall is transferred to an unresolved brine reservoir by a
 * volumetric source term.  No vapor or energy source is defined.
 *
 * Steady sink law
 * ---------------
 *   S_l = -rho_l * alpha_l * ramp / tau                 [kg m^-3 s^-1]
 *
 * CURRENT_TIMESTEP is intentionally not used: the documented Fluent
 * degassing example is transient, whereas setup 07b is steady.  The removal
 * time scale tau is therefore an explicit modeling parameter and must be
 * subjected to sensitivity testing.
 *
 * Hook placement for the Mixture model
 * ------------------------------------
 *   cwl_liquid_mass_sink  -> liquid phase mass source on cell zone "fluid"
 *   cwl_x_momentum_sink   -> mixture x-momentum source on "fluid"
 *   cwl_y_momentum_sink   -> mixture y-momentum source on "fluid"
 *   cwl_z_momentum_sink   -> mixture z-momentum source on "fluid"
 *   cwl_update_sink_mask  -> global Adjust hook
 *
 * Required Scheme/RP variables (created by the companion Python workflow)
 * -------------------------------------------------------------------------
 *   user/cwl07b/bottom-zone-id       integer
 *   user/cwl07b/liquid-phase-index   integer (zero-based sub-thread index)
 *   user/cwl07b/tau-s                real
 *   user/cwl07b/ramp                 real, bounded to [0,1]
 *   user/cwl07b/alpha-min            real, bounded to [0,1]
 */

#include "udf.h"

#define CWL_NUM_UDM 5
#define CWL_UDM_MASK 0
#define CWL_UDM_MASS_SOURCE 1
#define CWL_UDM_X_MOM_SOURCE 2
#define CWL_UDM_Y_MOM_SOURCE 3
#define CWL_UDM_Z_MOM_SOURCE 4

#define CWL_DEFAULT_BOTTOM_ZONE_ID (-1)
#define CWL_DEFAULT_LIQUID_PHASE_INDEX 1
#define CWL_DEFAULT_TAU_S 0.10
#define CWL_DEFAULT_RAMP 0.0
#define CWL_DEFAULT_ALPHA_MIN 1.0e-12

static int cwl_udm_offset = UDM_UNRESERVED;
static int cwl_bottom_zone_id = CWL_DEFAULT_BOTTOM_ZONE_ID;
static int cwl_liquid_phase_index = CWL_DEFAULT_LIQUID_PHASE_INDEX;
static real cwl_tau_s = CWL_DEFAULT_TAU_S;
static real cwl_ramp = CWL_DEFAULT_RAMP;
static real cwl_alpha_min = CWL_DEFAULT_ALPHA_MIN;

static real cwl_bound(real value, real lower, real upper)
{
    if (value < lower)
        return lower;
    if (value > upper)
        return upper;
    return value;
}

static int cwl_udm_is_ready(void)
{
    return cwl_udm_offset != UDM_UNRESERVED;
}

static real cwl_local_mass_source(cell_t c, Thread *mixture_thread,
                                  Thread *liquid_thread)
{
    real alpha;
    real density;

    if (!cwl_udm_is_ready())
        return 0.0;
    if (C_UDMI(c, mixture_thread, cwl_udm_offset + CWL_UDM_MASK) < 0.5)
        return 0.0;
    if (cwl_tau_s <= 0.0 || cwl_ramp <= 0.0)
        return 0.0;

    alpha = cwl_bound(C_VOF(c, liquid_thread), 0.0, 1.0);
    if (alpha <= cwl_alpha_min)
        return 0.0;

    density = C_R(c, liquid_thread);
    return -density * alpha * cwl_ramp / cwl_tau_s;
}

DEFINE_EXECUTE_ON_LOADING(cwl_reserve_and_name_udm, library_name)
{
    if (cwl_udm_offset == UDM_UNRESERVED)
        cwl_udm_offset = Reserve_User_Memory_Vars(CWL_NUM_UDM);

    if (cwl_udm_offset == UDM_UNRESERVED)
    {
        Message0("\nCWL07B ERROR: could not reserve %d UDM locations for %s.\n",
                 CWL_NUM_UDM, library_name);
        Message0("Allocate five additional UDMs and reload the library.\n");
        return;
    }

    Set_User_Memory_Name(cwl_udm_offset + CWL_UDM_MASK,
                         "cwl07b-bottom-adjacent-mask");
    Set_User_Memory_Name(cwl_udm_offset + CWL_UDM_MASS_SOURCE,
                         "cwl07b-liquid-mass-source-kgm3s");
    Set_User_Memory_Name(cwl_udm_offset + CWL_UDM_X_MOM_SOURCE,
                         "cwl07b-x-momentum-source-Nm3");
    Set_User_Memory_Name(cwl_udm_offset + CWL_UDM_Y_MOM_SOURCE,
                         "cwl07b-y-momentum-source-Nm3");
    Set_User_Memory_Name(cwl_udm_offset + CWL_UDM_Z_MOM_SOURCE,
                         "cwl07b-z-momentum-source-Nm3");

    Message0("\nCWL07B: reserved %d UDMs at offset %d for %s.\n",
             CWL_NUM_UDM, cwl_udm_offset, library_name);
}

DEFINE_ADJUST(cwl_update_sink_mask, mixture_domain)
{
    Thread *cell_thread;
    cell_t cell;
    face_t face;
    real adjacent_volume = 0.0;
    real adjacent_liquid_inventory = 0.0;
    real marked_cell_count = 0.0;

    /* RP variables are read on the host/serial process and then broadcast. */
#if !RP_NODE
    cwl_bottom_zone_id = RP_Get_Integer("user/cwl07b/bottom-zone-id");
    cwl_liquid_phase_index = RP_Get_Integer("user/cwl07b/liquid-phase-index");
    cwl_tau_s = RP_Get_Real("user/cwl07b/tau-s");
    cwl_ramp = RP_Get_Real("user/cwl07b/ramp");
    cwl_alpha_min = RP_Get_Real("user/cwl07b/alpha-min");
#endif

    host_to_node_int_3(cwl_bottom_zone_id, cwl_liquid_phase_index,
                       cwl_udm_offset);
    host_to_node_real_3(cwl_tau_s, cwl_ramp, cwl_alpha_min);

    cwl_ramp = cwl_bound(cwl_ramp, 0.0, 1.0);
    cwl_alpha_min = cwl_bound(cwl_alpha_min, 0.0, 1.0);

    if (!cwl_udm_is_ready())
    {
        Message0("CWL07B ERROR: UDM reservation is unavailable; sink remains off.\n");
        return;
    }
    if (cwl_bottom_zone_id < 0 || cwl_liquid_phase_index < 0 || cwl_tau_s <= 0.0)
    {
        Message0("CWL07B ERROR: invalid parameters: bottom=%d phase-index=%d tau=%g.\n",
                 cwl_bottom_zone_id, cwl_liquid_phase_index, cwl_tau_s);
        return;
    }

#if !RP_HOST
    /* Clear all diagnostics before reconstructing the one-cell boundary mask. */
    thread_loop_c(cell_thread, mixture_domain)
    {
        if (FLUID_THREAD_P(cell_thread))
        {
            begin_c_loop(cell, cell_thread)
            {
                C_UDMI(cell, cell_thread, cwl_udm_offset + CWL_UDM_MASK) = 0.0;
                C_UDMI(cell, cell_thread, cwl_udm_offset + CWL_UDM_MASS_SOURCE) = 0.0;
                C_UDMI(cell, cell_thread, cwl_udm_offset + CWL_UDM_X_MOM_SOURCE) = 0.0;
                C_UDMI(cell, cell_thread, cwl_udm_offset + CWL_UDM_Y_MOM_SOURCE) = 0.0;
                C_UDMI(cell, cell_thread, cwl_udm_offset + CWL_UDM_Z_MOM_SOURCE) = 0.0;
            }
            end_c_loop(cell, cell_thread)
        }
    }

    {
        Thread *bottom_thread = Lookup_Thread(mixture_domain, cwl_bottom_zone_id);
        if (bottom_thread == NULL)
        {
            Message0("CWL07B ERROR: bottom thread id %d was not found; sink remains off.\n",
                     cwl_bottom_zone_id);
            return;
        }

        begin_f_loop(face, bottom_thread)
        {
            cell_t adjacent_cell = F_C0(face, bottom_thread);
            Thread *adjacent_thread = F_C0_THREAD(face, bottom_thread);
            C_UDMI(adjacent_cell, adjacent_thread,
                   cwl_udm_offset + CWL_UDM_MASK) = 1.0;
        }
        end_f_loop(face, bottom_thread)
    }

    /* Owned-cell loop avoids double counting partition ghosts and repeated faces. */
    thread_loop_c(cell_thread, mixture_domain)
    {
        if (FLUID_THREAD_P(cell_thread))
        {
            Thread *liquid_thread =
                THREAD_SUB_THREAD(cell_thread, cwl_liquid_phase_index);
            begin_c_loop_int(cell, cell_thread)
            {
                if (C_UDMI(cell, cell_thread,
                           cwl_udm_offset + CWL_UDM_MASK) > 0.5)
                {
                    real cell_volume = C_VOLUME(cell, cell_thread);
                    real alpha = cwl_bound(C_VOF(cell, liquid_thread), 0.0, 1.0);
                    adjacent_volume += cell_volume;
                    adjacent_liquid_inventory +=
                        C_R(cell, liquid_thread) * alpha * cell_volume;
                    marked_cell_count += 1.0;
                }
            }
            end_c_loop_int(cell, cell_thread)
        }
    }

#if RP_NODE
    adjacent_volume = PRF_GRSUM1(adjacent_volume);
    adjacent_liquid_inventory = PRF_GRSUM1(adjacent_liquid_inventory);
    marked_cell_count = PRF_GRSUM1(marked_cell_count);
#endif
#endif /* !RP_HOST */

    node_to_host_real_3(adjacent_volume, adjacent_liquid_inventory,
                        marked_cell_count);
    Message0("CWL07B: bottom=%d phase-index=%d tau=%g s ramp=%g "
             "marked-cells=%.0f layer-volume=%g m3 liquid-inventory=%g kg\n",
             cwl_bottom_zone_id, cwl_liquid_phase_index, cwl_tau_s, cwl_ramp,
             marked_cell_count, adjacent_volume, adjacent_liquid_inventory);
}

DEFINE_SOURCE(cwl_liquid_mass_sink, cell, liquid_thread, dS, eqn)
{
    Thread *mixture_thread = THREAD_SUPER_THREAD(liquid_thread);
    real source = cwl_local_mass_source(cell, mixture_thread, liquid_thread);

    dS[eqn] = 0.0;
    if (!cwl_udm_is_ready())
        return 0.0;
    if (cwl_tau_s > 0.0 && cwl_ramp > 0.0 &&
        C_UDMI(cell, mixture_thread, cwl_udm_offset + CWL_UDM_MASK) > 0.5)
    {
        dS[eqn] = -C_R(cell, liquid_thread) * cwl_ramp / cwl_tau_s;
    }
    C_UDMI(cell, mixture_thread,
           cwl_udm_offset + CWL_UDM_MASS_SOURCE) = source;
    return source;
}

static real cwl_momentum_source(cell_t cell, Thread *mixture_thread,
                                int component)
{
    Thread *liquid_thread =
        THREAD_SUB_THREAD(mixture_thread, cwl_liquid_phase_index);
    real mass_source = cwl_local_mass_source(cell, mixture_thread, liquid_thread);
    real velocity = 0.0;
    real source;

    if (!cwl_udm_is_ready())
        return 0.0;

    if (component == 0)
        velocity = C_U(cell, mixture_thread);
    else if (component == 1)
        velocity = C_V(cell, mixture_thread);
#if RP_3D
    else if (component == 2)
        velocity = C_W(cell, mixture_thread);
#endif

    source = mass_source * velocity;
    if (component == 0)
        C_UDMI(cell, mixture_thread,
               cwl_udm_offset + CWL_UDM_X_MOM_SOURCE) = source;
    else if (component == 1)
        C_UDMI(cell, mixture_thread,
               cwl_udm_offset + CWL_UDM_Y_MOM_SOURCE) = source;
#if RP_3D
    else if (component == 2)
        C_UDMI(cell, mixture_thread,
               cwl_udm_offset + CWL_UDM_Z_MOM_SOURCE) = source;
#endif
    return source;
}

DEFINE_SOURCE(cwl_x_momentum_sink, cell, mixture_thread, dS, eqn)
{
    Thread *liquid_thread =
        THREAD_SUB_THREAD(mixture_thread, cwl_liquid_phase_index);
    real mass_source = cwl_local_mass_source(cell, mixture_thread, liquid_thread);
    dS[eqn] = mass_source;
    return cwl_momentum_source(cell, mixture_thread, 0);
}

DEFINE_SOURCE(cwl_y_momentum_sink, cell, mixture_thread, dS, eqn)
{
    Thread *liquid_thread =
        THREAD_SUB_THREAD(mixture_thread, cwl_liquid_phase_index);
    real mass_source = cwl_local_mass_source(cell, mixture_thread, liquid_thread);
    dS[eqn] = mass_source;
    return cwl_momentum_source(cell, mixture_thread, 1);
}

DEFINE_SOURCE(cwl_z_momentum_sink, cell, mixture_thread, dS, eqn)
{
    Thread *liquid_thread =
        THREAD_SUB_THREAD(mixture_thread, cwl_liquid_phase_index);
    real mass_source = cwl_local_mass_source(cell, mixture_thread, liquid_thread);
    dS[eqn] = mass_source;
#if RP_3D
    return cwl_momentum_source(cell, mixture_thread, 2);
#else
    return 0.0;
#endif
}
