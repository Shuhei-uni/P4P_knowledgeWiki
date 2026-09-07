/*
 * Setup 07c diagnostic: thickened constant-water-level liquid sink.
 *
 * The physical bottom boundary remains an impermeable no-slip wall.  Liquid
 * inside a fixed-height band immediately above that wall is transferred to an
 * unresolved reservoir through the same steady source law used by setup 07b:
 *
 *   S_l = -rho_l * alpha_l * ramp / tau                 [kg m^-3 s^-1]
 *
 * The fixed physical height avoids partition-dependent face-neighbour growth
 * and gives the mask a reproducible geometric meaning.  No vapor or energy
 * source is defined.  Mixture momentum is removed consistently with mass.
 *
 * Required RP variables:
 *   user/cwl07c/bottom-zone-id
 *   user/cwl07c/liquid-phase-index
 *   user/cwl07c/tau-s
 *   user/cwl07c/ramp
 *   user/cwl07c/alpha-min
 *   user/cwl07c/bottom-y-m
 *   user/cwl07c/layer-thickness-m
 */

#include "udf.h"

#define CWL07C_NUM_UDM 5
#define CWL07C_UDM_MASK 0
#define CWL07C_UDM_MASS_SOURCE 1
#define CWL07C_UDM_X_MOM_SOURCE 2
#define CWL07C_UDM_Y_MOM_SOURCE 3
#define CWL07C_UDM_Z_MOM_SOURCE 4

#define CWL07C_DEFAULT_BOTTOM_ZONE_ID (-1)
#define CWL07C_DEFAULT_LIQUID_PHASE_INDEX 1
#define CWL07C_DEFAULT_TAU_S 0.10
#define CWL07C_DEFAULT_RAMP 0.0
#define CWL07C_DEFAULT_ALPHA_MIN 1.0e-12
#define CWL07C_DEFAULT_BOTTOM_Y_M (-6.441)
#define CWL07C_DEFAULT_LAYER_THICKNESS_M 0.1401648
#define CWL07C_GEOMETRY_TOLERANCE_M 1.0e-8

static int cwl07c_udm_offset = UDM_UNRESERVED;
static int cwl07c_bottom_zone_id = CWL07C_DEFAULT_BOTTOM_ZONE_ID;
static int cwl07c_liquid_phase_index = CWL07C_DEFAULT_LIQUID_PHASE_INDEX;
static real cwl07c_tau_s = CWL07C_DEFAULT_TAU_S;
static real cwl07c_ramp = CWL07C_DEFAULT_RAMP;
static real cwl07c_alpha_min = CWL07C_DEFAULT_ALPHA_MIN;
static real cwl07c_bottom_y_m = CWL07C_DEFAULT_BOTTOM_Y_M;
static real cwl07c_layer_thickness_m = CWL07C_DEFAULT_LAYER_THICKNESS_M;

static real cwl07c_bound(real value, real lower, real upper)
{
    if (value < lower)
        return lower;
    if (value > upper)
        return upper;
    return value;
}

static int cwl07c_udm_is_ready(void)
{
    return cwl07c_udm_offset != UDM_UNRESERVED;
}

static void cwl07c_read_and_broadcast_controls(void)
{
#if !RP_NODE
    cwl07c_bottom_zone_id = RP_Get_Integer("user/cwl07c/bottom-zone-id");
    cwl07c_liquid_phase_index =
        RP_Get_Integer("user/cwl07c/liquid-phase-index");
    cwl07c_tau_s = RP_Get_Real("user/cwl07c/tau-s");
    cwl07c_ramp = RP_Get_Real("user/cwl07c/ramp");
    cwl07c_alpha_min = RP_Get_Real("user/cwl07c/alpha-min");
    cwl07c_bottom_y_m = RP_Get_Real("user/cwl07c/bottom-y-m");
    cwl07c_layer_thickness_m =
        RP_Get_Real("user/cwl07c/layer-thickness-m");
#endif

    host_to_node_int_3(cwl07c_bottom_zone_id, cwl07c_liquid_phase_index,
                       cwl07c_udm_offset);
    host_to_node_real_3(cwl07c_tau_s, cwl07c_ramp, cwl07c_alpha_min);
    host_to_node_real_2(cwl07c_bottom_y_m, cwl07c_layer_thickness_m);

    cwl07c_ramp = cwl07c_bound(cwl07c_ramp, 0.0, 1.0);
    cwl07c_alpha_min = cwl07c_bound(cwl07c_alpha_min, 0.0, 1.0);
}

static real cwl07c_local_mass_source(cell_t c, Thread *mixture_thread,
                                     Thread *liquid_thread)
{
    real alpha;
    real density;

    if (!cwl07c_udm_is_ready())
        return 0.0;
    if (C_UDMI(c, mixture_thread, cwl07c_udm_offset + CWL07C_UDM_MASK) < 0.5)
        return 0.0;
    if (cwl07c_tau_s <= 0.0 || cwl07c_ramp <= 0.0)
        return 0.0;

    alpha = cwl07c_bound(C_VOF(c, liquid_thread), 0.0, 1.0);
    if (alpha <= cwl07c_alpha_min)
        return 0.0;

    density = C_R(c, liquid_thread);
    return -density * alpha * cwl07c_ramp / cwl07c_tau_s;
}

DEFINE_EXECUTE_ON_LOADING(cwl07c_reserve_and_name_udm, library_name)
{
    if (cwl07c_udm_offset == UDM_UNRESERVED)
        cwl07c_udm_offset = Reserve_User_Memory_Vars(CWL07C_NUM_UDM);

    if (cwl07c_udm_offset == UDM_UNRESERVED)
    {
        Message0("\nCWL07C ERROR: could not reserve %d UDM locations for %s.\n",
                 CWL07C_NUM_UDM, library_name);
        return;
    }

    Set_User_Memory_Name(cwl07c_udm_offset + CWL07C_UDM_MASK,
                         "cwl07c-thick-bottom-mask");
    Set_User_Memory_Name(cwl07c_udm_offset + CWL07C_UDM_MASS_SOURCE,
                         "cwl07c-liquid-mass-source-kgm3s");
    Set_User_Memory_Name(cwl07c_udm_offset + CWL07C_UDM_X_MOM_SOURCE,
                         "cwl07c-x-momentum-source-Nm3");
    Set_User_Memory_Name(cwl07c_udm_offset + CWL07C_UDM_Y_MOM_SOURCE,
                         "cwl07c-y-momentum-source-Nm3");
    Set_User_Memory_Name(cwl07c_udm_offset + CWL07C_UDM_Z_MOM_SOURCE,
                         "cwl07c-z-momentum-source-Nm3");

    Message0("\nCWL07C: reserved %d UDMs at offset %d for %s.\n",
             CWL07C_NUM_UDM, cwl07c_udm_offset, library_name);
}

static void cwl07c_build_sink_mask(Domain *mixture_domain)
{
    Thread *cell_thread;
    cell_t cell;
    face_t face;
    real marked_volume = 0.0;
    real marked_liquid_inventory = 0.0;
    real marked_cell_count = 0.0;
    real face_y_min = 1.0e30;
    real face_y_max = -1.0e30;
    real marked_y_min = 1.0e30;
    real marked_y_max = -1.0e30;
    real dummy_one = 0.0;
    real dummy_two = 0.0;

    cwl07c_read_and_broadcast_controls();

    if (!cwl07c_udm_is_ready())
    {
        Message0("CWL07C ERROR: UDM reservation unavailable; sink remains off.\n");
        return;
    }
    if (cwl07c_bottom_zone_id < 0 || cwl07c_liquid_phase_index < 0 ||
        cwl07c_tau_s <= 0.0 || cwl07c_layer_thickness_m <= 0.0)
    {
        Message0("CWL07C ERROR: invalid controls bottom=%d phase=%d tau=%g "
                 "thickness=%g.\n",
                 cwl07c_bottom_zone_id, cwl07c_liquid_phase_index,
                 cwl07c_tau_s, cwl07c_layer_thickness_m);
        return;
    }

#if !RP_HOST
    {
        Thread *bottom_thread =
            Lookup_Thread(mixture_domain, cwl07c_bottom_zone_id);
        if (bottom_thread == NULL)
        {
            Message0("CWL07C ERROR: bottom thread id %d not found.\n",
                     cwl07c_bottom_zone_id);
            return;
        }
        begin_f_loop(face, bottom_thread)
        {
            real centroid[ND_ND];
            F_CENTROID(centroid, face, bottom_thread);
            if (centroid[1] < face_y_min)
                face_y_min = centroid[1];
            if (centroid[1] > face_y_max)
                face_y_max = centroid[1];
        }
        end_f_loop(face, bottom_thread)
    }

#if RP_NODE
    face_y_min = PRF_GRLOW1(face_y_min);
    face_y_max = PRF_GRHIGH1(face_y_max);
#endif

    thread_loop_c(cell_thread, mixture_domain)
    {
        if (FLUID_THREAD_P(cell_thread))
        {
            begin_c_loop(cell, cell_thread)
            {
                real centroid[ND_ND];
                real dy;
                C_CENTROID(centroid, cell, cell_thread);
                dy = centroid[1] - cwl07c_bottom_y_m;
                C_UDMI(cell, cell_thread,
                       cwl07c_udm_offset + CWL07C_UDM_MASK) =
                    (dy >= -CWL07C_GEOMETRY_TOLERANCE_M &&
                     dy <= cwl07c_layer_thickness_m) ? 1.0 : 0.0;
                C_UDMI(cell, cell_thread,
                       cwl07c_udm_offset + CWL07C_UDM_MASS_SOURCE) = 0.0;
                C_UDMI(cell, cell_thread,
                       cwl07c_udm_offset + CWL07C_UDM_X_MOM_SOURCE) = 0.0;
                C_UDMI(cell, cell_thread,
                       cwl07c_udm_offset + CWL07C_UDM_Y_MOM_SOURCE) = 0.0;
                C_UDMI(cell, cell_thread,
                       cwl07c_udm_offset + CWL07C_UDM_Z_MOM_SOURCE) = 0.0;
            }
            end_c_loop(cell, cell_thread)
        }
    }

    thread_loop_c(cell_thread, mixture_domain)
    {
        if (FLUID_THREAD_P(cell_thread))
        {
            Thread *liquid_thread =
                THREAD_SUB_THREAD(cell_thread, cwl07c_liquid_phase_index);
            begin_c_loop_int(cell, cell_thread)
            {
                if (C_UDMI(cell, cell_thread,
                           cwl07c_udm_offset + CWL07C_UDM_MASK) > 0.5)
                {
                    real centroid[ND_ND];
                    real cell_volume = C_VOLUME(cell, cell_thread);
                    real alpha = cwl07c_bound(
                        C_VOF(cell, liquid_thread), 0.0, 1.0);
                    C_CENTROID(centroid, cell, cell_thread);
                    marked_volume += cell_volume;
                    marked_liquid_inventory +=
                        C_R(cell, liquid_thread) * alpha * cell_volume;
                    marked_cell_count += 1.0;
                    if (centroid[1] < marked_y_min)
                        marked_y_min = centroid[1];
                    if (centroid[1] > marked_y_max)
                        marked_y_max = centroid[1];
                }
            }
            end_c_loop_int(cell, cell_thread)
        }
    }

#if RP_NODE
    marked_volume = PRF_GRSUM1(marked_volume);
    marked_liquid_inventory = PRF_GRSUM1(marked_liquid_inventory);
    marked_cell_count = PRF_GRSUM1(marked_cell_count);
    marked_y_min = PRF_GRLOW1(marked_y_min);
    marked_y_max = PRF_GRHIGH1(marked_y_max);
#endif
#endif /* !RP_HOST */

    node_to_host_real_3(marked_volume, marked_liquid_inventory,
                        marked_cell_count);
    node_to_host_real_3(face_y_min, face_y_max, marked_y_min);
    node_to_host_real_3(marked_y_max, dummy_one, dummy_two);

    Message0("CWL07C: bottom=%d phase-index=%d tau=%g s ramp=%g "
             "bottom-y=%g m face-y=[%g,%g] m thickness=%g m "
             "marked-cells=%.0f mask-volume=%g m3 marked-y=[%g,%g] m "
             "liquid-inventory=%g kg\n",
             cwl07c_bottom_zone_id, cwl07c_liquid_phase_index,
             cwl07c_tau_s, cwl07c_ramp, cwl07c_bottom_y_m,
             face_y_min, face_y_max, cwl07c_layer_thickness_m,
             marked_cell_count, marked_volume, marked_y_min,
             marked_y_max, marked_liquid_inventory);
}

DEFINE_ADJUST(cwl07c_update_sink_mask, mixture_domain)
{
    cwl07c_build_sink_mask(mixture_domain);
}

DEFINE_ON_DEMAND(cwl07c_rebuild_sink_mask)
{
    cwl07c_build_sink_mask(Get_Domain(1));
}

DEFINE_SOURCE(cwl07c_liquid_mass_sink, cell, liquid_thread, dS, eqn)
{
    Thread *mixture_thread = THREAD_SUPER_THREAD(liquid_thread);
    real source =
        cwl07c_local_mass_source(cell, mixture_thread, liquid_thread);

    dS[eqn] = 0.0;
    if (!cwl07c_udm_is_ready())
        return 0.0;
    if (cwl07c_tau_s > 0.0 && cwl07c_ramp > 0.0 &&
        C_UDMI(cell, mixture_thread,
               cwl07c_udm_offset + CWL07C_UDM_MASK) > 0.5)
    {
        dS[eqn] = -C_R(cell, liquid_thread) *
                   cwl07c_ramp / cwl07c_tau_s;
    }
    C_UDMI(cell, mixture_thread,
           cwl07c_udm_offset + CWL07C_UDM_MASS_SOURCE) = source;
    return source;
}

static real cwl07c_momentum_source(cell_t cell, Thread *mixture_thread,
                                   int component)
{
    Thread *liquid_thread =
        THREAD_SUB_THREAD(mixture_thread, cwl07c_liquid_phase_index);
    real mass_source =
        cwl07c_local_mass_source(cell, mixture_thread, liquid_thread);
    real velocity = 0.0;
    real source;

    if (!cwl07c_udm_is_ready())
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
               cwl07c_udm_offset + CWL07C_UDM_X_MOM_SOURCE) = source;
    else if (component == 1)
        C_UDMI(cell, mixture_thread,
               cwl07c_udm_offset + CWL07C_UDM_Y_MOM_SOURCE) = source;
#if RP_3D
    else if (component == 2)
        C_UDMI(cell, mixture_thread,
               cwl07c_udm_offset + CWL07C_UDM_Z_MOM_SOURCE) = source;
#endif
    return source;
}

DEFINE_SOURCE(cwl07c_x_momentum_sink, cell, mixture_thread, dS, eqn)
{
    Thread *liquid_thread =
        THREAD_SUB_THREAD(mixture_thread, cwl07c_liquid_phase_index);
    real mass_source =
        cwl07c_local_mass_source(cell, mixture_thread, liquid_thread);
    dS[eqn] = mass_source;
    return cwl07c_momentum_source(cell, mixture_thread, 0);
}

DEFINE_SOURCE(cwl07c_y_momentum_sink, cell, mixture_thread, dS, eqn)
{
    Thread *liquid_thread =
        THREAD_SUB_THREAD(mixture_thread, cwl07c_liquid_phase_index);
    real mass_source =
        cwl07c_local_mass_source(cell, mixture_thread, liquid_thread);
    dS[eqn] = mass_source;
    return cwl07c_momentum_source(cell, mixture_thread, 1);
}

DEFINE_SOURCE(cwl07c_z_momentum_sink, cell, mixture_thread, dS, eqn)
{
    Thread *liquid_thread =
        THREAD_SUB_THREAD(mixture_thread, cwl07c_liquid_phase_index);
    real mass_source =
        cwl07c_local_mass_source(cell, mixture_thread, liquid_thread);
    dS[eqn] = mass_source;
#if RP_3D
    return cwl07c_momentum_source(cell, mixture_thread, 2);
#else
    return 0.0;
#endif
}
