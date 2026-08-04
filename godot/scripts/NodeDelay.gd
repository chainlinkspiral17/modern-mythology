class_name NodeDelay
## Lifetime-bound delayed calls.
##
## `get_tree().create_timer(...)` lives on the SceneTree, so a pending
## timeout outlives the scene that scheduled it. A lambda connected to
## that timeout then fires with freed captures after the scene is
## quit — the "Lambda capture at index N was freed. Passed 'null'
## instead" console error. This helper parents a one-shot Timer to the
## scheduling node: the timer dies with the node and the callback can
## never fire after free.


static func after(host: Node, secs: float, cb: Callable) -> void:
	if host == null or not is_instance_valid(host) or not host.is_inside_tree():
		return
	var t := Timer.new()
	t.one_shot = true
	t.wait_time = maxf(secs, 0.001)
	host.add_child(t)
	t.timeout.connect(func() -> void:
		t.queue_free()
		if cb.is_valid():
			cb.call())
	t.start()
