/*
 * LazyList.java
 *
 * Created on January 4, 2006, 1:41 PM
 *
 * From "Multiprocessor Synchronization and Concurrent Data Structures",
 * by Maurice Herlihy and Nir Shavit.
 * Copyright 2006 Elsevier Inc. All rights reserved.
 */

package lists;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class LazyList<T> {
  private Node head;
  public LazyList() {
    // Add sentinels to start and end
    this.head  = new Node(Integer.MIN_VALUE);
    this.head.next = new Node(Integer.MAX_VALUE);
  }
  
  private boolean validate(Node pred, Node curr) {
    return  !pred.marked && !curr.marked && pred.next == curr;
  }

  public boolean add(T item) {
    int key = item.hashCode();
    while (true) {
      Node pred = this.head;
      Node curr = head.next;
      while (curr.key < key) {
        pred = curr; curr = curr.next;
      }
      pred.lock();
      try {
        curr.lock();
        try {
          if (validate(pred, curr)) {
            if (curr.key == key) { // present
              return false;
            } else {               // not present
              Node Node = new Node(item);
              Node.next = curr;
              pred.next = Node;
              return true;
            }
          }
        } finally { // always unlock
          curr.unlock();
        }
      } finally { // always unlock
        pred.unlock();
      }
    }
  }

  public boolean remove(T item) {
    int key = item.hashCode();
    while (true) {
      Node pred = this.head;
      Node curr = head.next;
      while (curr.key < key) {
        pred = curr; curr = curr.next;
      }
      pred.lock();
      try {
        curr.lock();
        try {
          if (validate(pred, curr)) {
            if (curr.key != key) {    // present
              return false;
            } else {                  // absent
              curr.marked = true;     // logically remove
              pred.next = curr.next;  // physically remove
              return true;
            }
          }
        } finally {                   // always unlock curr
          curr.unlock();
        }
      } finally {                     // always unlock pred
        pred.unlock();
      }
    }
  }

  public boolean contains(T item) {
    int key = item.hashCode();
    Node curr = this.head;
    while (curr.key < key)
      curr = curr.next;
    return curr.key == key && !curr.marked;
  }

  private class Node {
    T item;
    int key;
    Node next;
    boolean marked;
    Lock lock;
    Node(T item) {      // usual constructor
      this.item = item;
      this.key = item.hashCode();
      this.next = null;
      this.marked = false;
      this.lock = new ReentrantLock();
    }
    Node(int key) { // sentinel constructor
      this.item = null;
      this.key = key;
      this.next = null;
      this.marked = false;
      this.lock = new ReentrantLock();
    }
    void lock() {lock.lock();}
    void unlock() {lock.unlock();}
  }
}

