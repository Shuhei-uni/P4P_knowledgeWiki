/* Read-only Fluent 25.2 EWF storage probe for the verified 60,964-cell pilot.
 * Wall IDs 33 (wall) and 4 (wall:004) come from its native case topology.
 * No hooks, sources, field assignments, RP writes or tracking calls.
 * Report each available storage separately; unavailable storage is not zero.
 */
#include "udf.h"
#include "sg_film.h"

DEFINE_ON_DEMAND(phase72a_ewf_source_probe)
{
#if !RP_HOST
    Domain *domain = Get_Domain(1);
    int walls[2] = {33, 4};
    Svar vars[9] = {SV_EFILM_PHS2_MASS_SRC, SV_EFILM_DPM_MASS_SRC,
        SV_EFILM_SEPARATING_SRC, SV_EFILM_STRIPPING_SRC,
        SV_EFILM_SEPARATED_MASS, SV_EFILM_STRIPPED_MASS,
        SV_EFILM_SEPARATED_MASS_SUM, SV_EFILM_STRIPPED_MASS_SUM,
        SV_EFILM_MASS_PHS2_S};
    int w, phase, k;
    for (w = 0; w < 2; ++w)
    {
        Thread *mixture = NNULLP(domain) ? Lookup_Thread(domain, walls[w]) : NULL;
        for (phase = -1; phase < 2; ++phase)
        {
            Thread *thread = NNULLP(mixture) ?
                (phase < 0 ? mixture : THREAD_SUB_THREAD(mixture, phase)) : NULL;
            int counts[9] = {0};
            real sums[9] = {0}, area_sums[9] = {0};
            face_t face;
            if (NNULLP(thread))
            {
                begin_f_loop(face, thread)
                {
#if RP_NODE
                    if (!PRINCIPAL_FACE_P(face, thread)) continue;
#endif
                    real area[ND_ND], magnitude;
                    F_AREA(area, face, thread);
                    magnitude = NV_MAG(area);
                    for (k = 0; k < 9; ++k)
                        if (NNULLP(THREAD_STORAGE(thread, vars[k])))
                        {
                            real value = F_STORAGE_R(face, thread, vars[k]);
                            counts[k] += 1;
                            sums[k] += value;
                            area_sums[k] += value * magnitude;
                        }
                }
                end_f_loop(face, thread)
            }
            for (k = 0; k < 9; ++k)
            {
#if RP_NODE
                counts[k] = PRF_GISUM1(counts[k]);
                sums[k] = PRF_GRSUM1(sums[k]);
                area_sums[k] = PRF_GRSUM1(area_sums[k]);
#endif
                Message0("P72_EWF_STORAGE iteration=%d wall=%d phase_index=%d variable_index=%d count=%d sum=%.17g area_sum=%.17g\n",
                    N_ITER, walls[w], phase, k, counts[k], sums[k], area_sums[k]);
            }
        }
    }
    /* The coupling source is a cell storage, not an EWF face storage. Read
     * mixture and phase cells separately; give both raw and volume sums so
     * the caller can establish the native source units from matched rates.
     */
    for (phase = -1; phase < 2; ++phase)
    {
        Thread *mixture_cell;
        int count = 0;
        real sum = 0, volume_sum = 0, positive_volume_sum = 0, negative_volume_sum = 0;
        thread_loop_c(mixture_cell, domain)
        {
            if (!FLUID_THREAD_P(mixture_cell)) continue;
            Thread *thread = phase < 0 ? mixture_cell : THREAD_SUB_THREAD(mixture_cell, phase);
            cell_t cell;
            if (NNULLP(thread) && NNULLP(THREAD_STORAGE(thread, SV_EFILM_MASS_PHS2_S)))
            {
                begin_c_loop_int(cell, thread)
                {
                    real value = C_STORAGE_R(cell, thread, SV_EFILM_MASS_PHS2_S);
                    real weighted = value * C_VOLUME(cell, mixture_cell);
                    ++count;
                    sum += value;
                    volume_sum += weighted;
                    if (weighted > 0) positive_volume_sum += weighted;
                    else negative_volume_sum += weighted;
                }
                end_c_loop_int(cell, thread)
            }
        }
#if RP_NODE
        count = PRF_GISUM1(count);
        sum = PRF_GRSUM1(sum);
        volume_sum = PRF_GRSUM1(volume_sum);
        positive_volume_sum = PRF_GRSUM1(positive_volume_sum);
        negative_volume_sum = PRF_GRSUM1(negative_volume_sum);
#endif
        Message0("P72_EWF_CELL_STORAGE iteration=%d phase_index=%d count=%d sum=%.17g volume_sum=%.17g positive_volume_sum=%.17g negative_volume_sum=%.17g\n",
            N_ITER, phase, count, sum, volume_sum, positive_volume_sum, negative_volume_sum);
    }
#endif
}
