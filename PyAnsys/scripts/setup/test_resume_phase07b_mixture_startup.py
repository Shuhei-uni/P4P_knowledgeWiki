"""File-only recovery guards; no Fluent import side effects or API connection."""
from pathlib import Path
import tempfile
import unittest
from resume_phase07b_mixture_startup import joined_conditioning_residuals,scalar_prefix_parity,ACTIVE_FLOW


class RecoveryPrefixes(unittest.TestCase):
    def residuals(self,path,indices,changed=None):
        names=sorted(ACTIVE_FLOW);lines=['iter '+' '.join(names)+' time/iter']
        for n in indices:lines.append(str(n)+' '+' '.join([str(.2 if n==changed else .1)]*6)+' 0:00:01 1')
        path.write_text('\n'.join(lines)+'\n')

    def test_exact_boundary_and_no_boundary_both_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);self.residuals(p/'prefix',range(1,51))
            for first in [50,51]:
                self.residuals(p/'segment',range(first,201))
                data,_=joined_conditioning_residuals(p/'prefix',p/'segment',p/f'combined{first}',200)
                self.assertEqual(data['iteration'].tolist(),list(range(1,201)))

    def test_changed_boundary_gap_or_wrong_restart_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);self.residuals(p/'prefix',range(1,51))
            for k,indices,changed in [(0,range(50,201),50),(1,range(52,201),None),(2,range(49,201),None),(3,list(range(51,100))+list(range(101,201)),None)]:
                self.residuals(p/'segment',indices,changed)
                with self.assertRaises(AssertionError):joined_conditioning_residuals(p/'prefix',p/'segment',p/f'combined{k}',200)

    def scalar(self,path,indices,changed=None):
        path.write_text('(\"Iteration\" \"sample\")\n'+'\n'.join(f'{n} {999 if n==changed else n*.1}' for n in indices)+'\n')

    def test_continuous_native_scalar_keeps_exact_prefix(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);self.scalar(p/'prefix',range(1,51));self.scalar(p/'native',range(1,201))
            data,_=scalar_prefix_parity(p/'prefix',p/'native',200);self.assertEqual(len(data['iteration']),200)
            self.scalar(p/'native',range(1,201),50)
            with self.assertRaises(AssertionError):scalar_prefix_parity(p/'prefix',p/'native',200)
            self.scalar(p/'native',range(51,201))
            with self.assertRaises(AssertionError):scalar_prefix_parity(p/'prefix',p/'native',200)


if __name__=='__main__':unittest.main()
