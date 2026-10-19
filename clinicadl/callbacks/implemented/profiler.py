from __future__ import annotations


from ..base import Callback
import torch.profiler as profiler
if TYPE_CHECKING:
    from clinicadl.io.maps import Maps

class ProfilerCallback(Callback):

    def __init__(
        self,
        num_measurements: int = 100,
        warmup_iterations: int = 10,
        with_stack: bool = False,
    ):
    self.num_measurements = num_measurements
    self.warmup_iterations = warmup_iterations
    self.with_stack = with_stack

    def on_trainer_init(self, maps: Maps, computational: ComputationalConfig):
        to_monitor = [profiler.ProfilerActivity.CPU]
        if computational.gpu:
            to_monitor.append(profiler.ProfilerActivity.CUDA)
        self.prof = profiler.profile(
        activities=to_monitor,
        schedule=profiler.schedule(skip_first=1, warmup=self.warmup_iterations, active=self.num_measurements),
        on_trace_ready=profiler.tensorboard_trace_handler(maps.training.splits[state.split_idx].logs.profiler),
        profile_memory=True,
        with_stack=True)

    def on_train_start(self, ):
        self.prof.start()

    def on_train_end(self, ):
        self.prof.stop()

    def on_batch_end(self, ):
        self.prof.step()
    

# Resume ?
# Predict et test ? (et val ?) -> où save les logs ? étendre monitor à ces deux phases ?
# Préciser différences entre Profiler et Monitor. Profilor -> débuggage
# Désactiver Monitor par défaut (donc déprécier "enabled" ?) ou baisser le nombre de measurements
# Monitor avec 0 measurements ?
