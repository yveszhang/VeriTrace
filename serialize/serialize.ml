open List
open Printf
open Array 
open Random

type time_stamp_t = int
type method_id_t = int
type thread_id_t = int 
type ret_value_t = int

type event_t = 
  | Call of time_stamp_t * method_id_t * thread_id_t
  | Retn of time_stamp_t * method_id_t * thread_id_t * ret_value_t
  | Method of (time_stamp_t * time_stamp_t) * method_id_t * thread_id_t * ret_value_t

type thread_state_t = Idle | Pending of time_stamp_t * method_id_t

let dummy_event = Call (-1, -1, -1)

let print_event ev = 
  match ev with
    | Call (ts, mid, tid) ->
      Printf.printf "%d: T%d call %d\n" ts tid mid 
    | Retn (ts, mid, tid, _) ->
      Printf.printf "%d: T%d return %d\n" ts tid mid
    | Method ((ts1, ts2), mid, tid, _) -> 
      Printf.printf "%d -- %d: T%d executes %d\n" ts1 ts2 tid mid

let rec list_remove_nth l n = 
  match l with 
    | [] -> []
    | x :: xs -> 
      if n < 0 then l else if n = 0 then xs else x :: list_remove_nth xs (n-1) 

let rec list_split_at_nth l n = 
  match l with 
    | [] -> ([], []) 
    | x :: xs -> 
      if n <= 0 then ([], l) else 
	let (l1, l2) = list_split_at_nth xs (n-1) in (x :: l1, l2) 

let rec interval n1 n2 = (* not including n2 *)
  if n1 >= n2  then [] else n1 :: interval (n1+1) n2

let rec list_interleave ls = 
(* ls is a list of lists. list_merge produces all possible interleaving of the lists in ls *)
  let lss = List.filter (fun x -> x <> []) ls in 
  match lss with 
    | [] -> [] 
    | [l] -> [l]
    | _ -> 
      let remove_nth_head ls n = 
	let (l1, l2) = list_split_at_nth ls n in 
	let h = List.hd (List.hd l2) in 
	let l2' = List.tl (List.hd l2) :: List.tl l2 in 
	(h, l1 @ l2') 
      in 
      let nth_head_interleave ls n = 
	let (h, ls') = remove_nth_head ls n in 
	List.map (fun x -> h :: x) (list_interleave ls')
      in 
      List.concat (List.map (nth_head_interleave lss) (interval 0 (List.length lss)))
;;	
      
let remove_pending_events events thread_num = 
  let arr_pending = Array.make thread_num (-1) in 
  let update i ev = 
    match ev with 
      | Call (_, _, tid) -> arr_pending.(tid) <- i 
      | Retn (_, _, tid, _) -> arr_pending.(tid) <- (-1) 
      | _ -> ()
  in
  let remove_pending idx = if idx >= 0 then events.(idx) <- Call (-1, -1, -1) else () in 
  let _ = 
    Array.iteri update events
    ; Array.iter remove_pending arr_pending 
    (* ; Array.iteri (fun i x -> match x with Call (_, -1, -1) -> () | _ -> (Printf.printf "%d: " i; print_event x)) events *)
  in 
  List.filter (fun x -> x <> Call (-1, -1, -1)) (Array.to_list events)
;;
  
let partition_sequence events method_num thread_num = 
(* events is a list, not an array *)
  let arr_thread = Array.make thread_num Idle in 
  let all_idle () = Array.fold_left (fun b ts -> if ts = Idle then b && true else b && false) true arr_thread in 
  let fold_fun parts ev = 
    let (es, ps) = parts in 
    match ev with 
      | Call (ts, mid, tid) -> 
	let _ = arr_thread.(tid) <- Pending (ts, mid) in (es, ps) 
      | Retn (ts, mid, tid, v) -> 
	let ts0 = match arr_thread.(tid) with Pending (ts', _) -> ts' | _ -> -1 in 
	let _ = arr_thread.(tid) <- Idle in 
	let es' = Method ((ts0, ts), mid, tid, v) :: es in 
	if all_idle () then ([], List.rev es' :: ps) else (es', ps) 
      | _ -> (es, ps) 
  in 
  List.rev (snd (List.fold_left fold_fun ([], []) events))
;;

let serialize events method_num thread_num = 
  let segs = partition_sequence (remove_pending_events events thread_num) method_num thread_num in 
  let _ = List.iter (fun es -> print_endline "****************"; List.iter print_event es;) segs in 
  let seg_serialize seg = 
    let arr_events = Array.make thread_num [] in 
    let register_event ev = 
      match ev with 
	| Call (_, _, tid) | Retn (_, _, tid, _) | Method (_, _, tid, _) -> 
	  arr_events.(tid) <- ev :: arr_events.(tid) 
    in 
    let _ = List.iter register_event seg in 
    list_interleave (Array.to_list (Array.map List.rev arr_events))
  in 
  List.map seg_serialize segs
;;


let generate_events method_num thread_num event_num = 
  let arr_thread = Array.make thread_num Idle in 
  let arr_event = Array.make event_num dummy_event in 
  let gen_a_event ts  = 
    let tid = Random.int thread_num in 
    let mid = Random.int method_num in 
    match arr_thread.(tid) with 
      | Idle -> 
	let _ = arr_thread.(tid) <- Pending (-1, mid) in 
	Call (ts, mid, tid)
      | Pending (_, mid') -> 
	let _ = arr_thread.(tid) <- Idle in 
	Retn (ts, mid', tid, 0) 
  in 
  let _ = for i = 0 to event_num-1 do arr_event.(i) <- gen_a_event i done in 
  arr_event
;;

let main () =
  let _ = Random.self_init () in
  let method_num = int_of_string Sys.argv.(1) in
  let thread_num = int_of_string Sys.argv.(2) in
  let event_num = int_of_string Sys.argv.(3) in
  let events = generate_events method_num thread_num event_num in 
  let _ =   for i = 0 to event_num-1 do print_event events.(i) done in 
  (* let segs = partition_sequence (remove_pending_events events thread_num) method_num thread_num in  *)
  let seqs = serialize events method_num thread_num in 
  List.iter (fun sqs -> print_endline "****************"; List.iter (fun es -> print_endline "----------"; List.iter print_event es) sqs) seqs
;;

main () ;;
