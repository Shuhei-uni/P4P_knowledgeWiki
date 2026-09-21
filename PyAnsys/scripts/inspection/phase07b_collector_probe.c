/*
 * Phase 7b: read-only geometry and storage-allocation diagnostic for Fluent 252.
 * Execute phase07b_collector_probe on demand after loading the approved mesh
 * and enabling the approved Mixture model. Initialization is NOT required.
 * No sources, field writes, UDMs, RP-variable writes, or solver calls exist here.
 *
 * Tops: Project/experiments/phase-07b-full-geometry-liquid-removal/
 *       geometry-proof.md, "Numerical lower datum and approved height fractions".
 * These are the approved y_b + f*(y_c-y_b) tops, in metres. Counts use whole
 * owned fluid cells whose Fluent centroid satisfies y <= top. They are
 * diagnostic selections, not cut-cell volumes or a physical-source definition.
 * The driver must separately verify the loaded artifact identity and units.
 *
 * Official 2025 R2 documentation for the macros used:
 * https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/flu_udf_sec_using_udfs_parallel.html
 * https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/flu_udf_GenPurposeLoopingMacros.html
 * https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_udf/flu_udf_DataAccessMacros.html
 *
 * begin_c_loop_int excludes partition ghosts. All collectives are called by
 * every compute node in the same order, after all local loops. The host does
 * not access mesh/storage. Message0 emits one set of JSON records from node 0
 * (or the serial process). No phase field is dereferenced, even if allocated.
 * Allocation therefore does NOT establish phase-velocity semantics or validity.
 */

#include "udf.h"
#include <float.h>
#include <math.h>

#define P7B_TOP_COUNT 5
#define P7B_LIQUID_INDEX 1
#define P7B_EXPECTED_CELLS 620431

#if !RP_HOST
static const real p7b_tops[P7B_TOP_COUNT] = {
    -1.1836669883728028,
    -0.8827502412796020,
    -0.5818334941864014,
    -0.2809167470932006,
     0.0200000000000000
};

/* Array entries count owned cells covered by the corresponding allocation. */
enum p7b_storage_index {
    P7B_LIQUID_PRESENT,
    P7B_SV_U,
    P7B_SV_V,
    P7B_SV_W,
    P7B_SV_DENSITY,
    P7B_SV_VOF,
    P7B_STORAGE_COUNT
};
#endif

DEFINE_ON_DEMAND(phase07b_collector_probe)
{
#if !RP_HOST
    Domain *domain = Get_Domain(1);
    Thread *thread;
    Thread *phase_thread;
    Thread *liquid_thread;
    cell_t cell;
    int i, phase_index;
    int domain_present_all = NNULLP(domain) ? 1 : 0;
    int data_valid_all = Data_Valid_P() ? 1 : 0;
    int data_valid_any = data_valid_all;
    int owned_cells = 0;
    int valid_geometry_cells = 0;
    int invalid_geometry_cells = 0;
    int owned_fluid_thread_instances = 0;
    int selected_cells[P7B_TOP_COUNT] = {0};
    int storage_cells[P7B_STORAGE_COUNT] = {0};
    real volume = 0.0;
    real selected_volume[P7B_TOP_COUNT] = {0.0};
    real min_y = (real)FLT_MAX;
    real max_y = -(real)FLT_MAX;

    if (NNULLP(domain))
    {
        thread_loop_c(thread, domain)
        {
            int thread_owned_cells = 0;
            int present[P7B_STORAGE_COUNT] = {0};

            if (!FLUID_THREAD_P(thread))
                continue;

            /* Enumerate existing subthreads; do not index an unproved array. */
            liquid_thread = NULL;
            if (NNULLP(THREAD_SUB_THREADS(thread)))
            {
                sub_thread_loop(phase_thread, thread, phase_index)
                {
                    if (phase_index == P7B_LIQUID_INDEX)
                        liquid_thread = phase_thread;
                }
            }
            if (NNULLP(liquid_thread))
            {
                present[P7B_LIQUID_PRESENT] = 1;
                present[P7B_SV_U] = NNULLP(THREAD_STORAGE(liquid_thread, SV_U)) ? 1 : 0;
                present[P7B_SV_V] = NNULLP(THREAD_STORAGE(liquid_thread, SV_V)) ? 1 : 0;
#if RP_3D
                present[P7B_SV_W] = NNULLP(THREAD_STORAGE(liquid_thread, SV_W)) ? 1 : 0;
#endif
                /* C_R uses SV_DENSITY; there is no assumed SV_R symbol. */
                present[P7B_SV_DENSITY] = NNULLP(THREAD_STORAGE(liquid_thread, SV_DENSITY)) ? 1 : 0;
                present[P7B_SV_VOF] = NNULLP(THREAD_STORAGE(liquid_thread, SV_VOF)) ? 1 : 0;
            }

            begin_c_loop_int(cell, thread)
            {
                real centroid[ND_ND];
                real cell_volume;
                int finite_centroid = 1;

                ++owned_cells;
                ++thread_owned_cells;
                C_CENTROID(centroid, cell, thread);
                cell_volume = C_VOLUME(cell, thread);
                for (i = 0; i < ND_ND; ++i)
                    if (!isfinite((double)centroid[i]))
                        finite_centroid = 0;
                if (!finite_centroid || !isfinite((double)cell_volume) || cell_volume <= 0.0)
                {
                    ++invalid_geometry_cells;
                    continue;
                }

                ++valid_geometry_cells;
                volume += cell_volume;
                if (centroid[1] < min_y) min_y = centroid[1];
                if (centroid[1] > max_y) max_y = centroid[1];
                for (i = 0; i < P7B_TOP_COUNT; ++i)
                {
                    if (centroid[1] <= p7b_tops[i])
                    {
                        ++selected_cells[i];
                        selected_volume[i] += cell_volume;
                    }
                }
            }
            end_c_loop_int(cell, thread)

            if (thread_owned_cells > 0)
                ++owned_fluid_thread_instances;
            for (i = 0; i < P7B_STORAGE_COUNT; ++i)
                storage_cells[i] += present[i] * thread_owned_cells;
        }
    }

    /* No early return above: empty partitions still join every collective. */
#if RP_NODE
    domain_present_all = PRF_GILOW1(domain_present_all);
    data_valid_all = PRF_GILOW1(data_valid_all);
    data_valid_any = PRF_GIHIGH1(data_valid_any);
    owned_cells = PRF_GISUM1(owned_cells);
    valid_geometry_cells = PRF_GISUM1(valid_geometry_cells);
    invalid_geometry_cells = PRF_GISUM1(invalid_geometry_cells);
    owned_fluid_thread_instances = PRF_GISUM1(owned_fluid_thread_instances);
    volume = PRF_GRSUM1(volume);
    min_y = PRF_GRLOW1(min_y);
    max_y = PRF_GRHIGH1(max_y);
    for (i = 0; i < P7B_TOP_COUNT; ++i)
    {
        selected_cells[i] = PRF_GISUM1(selected_cells[i]);
        selected_volume[i] = PRF_GRSUM1(selected_volume[i]);
    }
    for (i = 0; i < P7B_STORAGE_COUNT; ++i)
        storage_cells[i] = PRF_GISUM1(storage_cells[i]);
#endif

    Message0("PHASE07B_PROBE {\"record\":\"scope\",\"schema_version\":1,"
             "\"diagnostic_only\":true,\"selection\":\"owned_fluid_cell_centroid_y_le_top\","
             "\"dimensions\":%d,\"phase_velocity_semantics_verified\":false}\n", ND_ND);
    Message0("PHASE07B_PROBE {\"record\":\"baseline\",\"domain_present_all\":%d,"
             "\"data_valid_all\":%d,\"data_valid_any\":%d,\"owned_cells\":%d,"
             "\"expected_owned_cells\":%d,\"cell_count_matches_expected\":%d,"
             "\"valid_geometry_cells\":%d,\"invalid_geometry_cells\":%d,"
             "\"owned_fluid_thread_instances\":%d,\"valid_geometry_volume_m3\":%.17g}\n",
             domain_present_all, data_valid_all, data_valid_any, owned_cells,
             P7B_EXPECTED_CELLS, owned_cells == P7B_EXPECTED_CELLS,
             valid_geometry_cells, invalid_geometry_cells,
             owned_fluid_thread_instances, (double)volume);
    if (valid_geometry_cells > 0)
        Message0("PHASE07B_PROBE {\"record\":\"centroid_bounds\",\"min_y_m\":%.17g,\"max_y_m\":%.17g}\n",
                 (double)min_y, (double)max_y);
    else
        Message0("PHASE07B_PROBE {\"record\":\"centroid_bounds\",\"min_y_m\":null,\"max_y_m\":null}\n");
    for (i = 0; i < P7B_TOP_COUNT; ++i)
        Message0("PHASE07B_PROBE {\"record\":\"collector_geometry\",\"height_percent\":%d,"
                 "\"top_y_m\":%.17g,\"owned_cells\":%d,\"volume_m3\":%.17g}\n",
                 20 * (i + 1), (double)p7b_tops[i], selected_cells[i], (double)selected_volume[i]);
    Message0("PHASE07B_PROBE {\"record\":\"liquid_storage\",\"expected_phase_index\":%d,"
             "\"phase_identity_verified\":false,\"values_dereferenced\":false,"
             "\"denominator_owned_cells\":%d,\"cells_with_subthread\":%d,"
             "\"cells_with_SV_U\":%d,\"cells_with_SV_V\":%d,\"cells_with_SV_W\":%d,"
             "\"SV_W_applicable\":%d,\"cells_with_SV_DENSITY\":%d,\"cells_with_SV_VOF\":%d}\n",
             P7B_LIQUID_INDEX, owned_cells, storage_cells[P7B_LIQUID_PRESENT],
             storage_cells[P7B_SV_U], storage_cells[P7B_SV_V], storage_cells[P7B_SV_W],
             ND_ND == 3, storage_cells[P7B_SV_DENSITY], storage_cells[P7B_SV_VOF]);
    Message0("PHASE07B_PROBE {\"record\":\"end\",\"inspection_complete\":true,\"source_readiness_verified\":false}\n");
#endif
}
