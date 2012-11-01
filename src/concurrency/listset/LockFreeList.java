/*
 * LockFreeList.java
 *
 * Created on January 4, 2006, 2:41 PM
 *
 * From "Multiprocessor Synchronization and Concurrent Data Structures",
 * by Maurice Herlihy and Nir Shavit.
 * Copyright 2006 Elsevier Inc. All rights reserved.
 */

package concurrency ;

import java.util.concurrent.atomic.AtomicMarkableReference;

public class LockFreeList<T> {
  Node head;

  public LockFreeList() {
    this.head  = new Node(Integer.MIN_VALUE);
    Node tail = new Node(Integer.MAX_VALUE);
    while (!head.next.compareAndSet(null, tail, false, false));
  }

  public LockFreeList<T> clone() {
      LockFreeList<T> l = new LockFreeList<T>() ;
      Node curr = head.next.getReference() ;
      while (curr.key < Integer.MAX_VALUE) {
	  l.add(curr.item) ;
	  curr = curr.next.getReference() ;
      }
      return l ;
  }

  public String toString() {
      String s = "{" ;
      Node curr = head.next.getReference() ;
      while (curr.key < Integer.MAX_VALUE) {
	  s = s + curr.item.toString() ;
	  curr = curr.next.getReference() ;
	  if (curr.key != Integer.MAX_VALUE) 
	      s = s + ", " ;
      }
      s = s + "}" ;
      return s ;
  }

  public boolean add(T item) {
    int key = item.hashCode();
    boolean splice;
    while (true) {
      // find predecessor and curren entries
      Window window = find(head, key);
      Node pred = window.pred, curr = window.curr;
      // is the key present?
      if (curr.key == key) {
        return false;
      } else {
        // splice in new node
        Node node = new Node(item);
        node.next = new AtomicMarkableReference(curr, false);
        if (pred.next.compareAndSet(curr, node, false, false)) {
          return true;
        }
      }
    }
  }

  public boolean remove(T item) {
    int key = item.hashCode();
    boolean snip;
    while (true) {
      // find predecessor and curren entries
      Window window = find(head, key);
      Node pred = window.pred, curr = window.curr;
      // is the key present?
      if (curr.key != key) {
        return false;
      } else {
        // snip out matching node
        Node succ = curr.next.getReference();
        snip = curr.next.attemptMark(succ, true);
        if (!snip)
          continue;
        pred.next.compareAndSet(curr, succ, false, false);
        return true;
      }
    }
  }

  public boolean contains(T item) {
    int key = item.hashCode();
    // find predecessor and curren entries
    Window window = find(head, key);
    Node pred = window.pred, curr = window.curr;
    return (curr.key == key);
  }

  private class Node {
    T item;
    int key;
    AtomicMarkableReference<Node> next;
    Node(T item) {      // usual constructor
      this.item = item;
      this.key = item.hashCode();
      this.next = new AtomicMarkableReference<Node>(null, false);
    }
    Node(int key) { // sentinel constructor
      this.item = null;
      this.key = key;
      this.next = new AtomicMarkableReference<Node>(null, false);
    }
  }
  
  class Window {
    public Node pred;
    public Node curr;
    Window(Node pred, Node curr) {
      this.pred = pred; this.curr = curr;
    }
  }
  
  public Window find(Node head, int key) {
    Node pred = null, curr = null, succ = null;
    boolean[] marked = {false}; // is curr marked?
    boolean snip;
    retry: while (true) {
      pred = head;
      curr = pred.next.getReference();
      while (true) {
        succ = curr.next.get(marked); 
        while (marked[0]) {           // replace curr if marked
          snip = pred.next.compareAndSet(curr, succ, false, false);
          if (!snip) continue retry;
          curr = pred.next.getReference();
          succ = curr.next.get(marked);
        }
        if (curr.key >= key)
          return new Window(pred, curr);
        pred = curr;
        curr = succ;
      }
    }
  }
}
