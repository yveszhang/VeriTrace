/*
 * CoarseList.java
 *
 * Created on January 3, 2006, 5:02 PM
 *
 * From "Multiprocessor Synchronization and Concurrent Data Structures",
 * by Maurice Herlihy and Nir Shavit.
 * Copyright 2006 Elsevier Inc. All rights reserved.
 *
 * Modified by ZHANG Yu
 */
package concurrency;
import java.util.Collection ;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class CoarseList<T> {

  private class Node<T> {
    T item;
    int key;
    Node next;
    Node(T item) {
      this.item = item;
      this.key = item.hashCode();
    }
    Node(int key) {
      this.item = null;
      this.key = key;
    }
  }

  private Node head;
  private Node tail;
  private Lock lock = new ReentrantLock();
  
  public CoarseList() {
    // Add sentinels to start and end
    head  = new Node(Integer.MIN_VALUE);
    tail  = new Node(Integer.MAX_VALUE);
    head.next = this.tail;
  }


  public CoarseList<T> clone() {
      CoarseList<T> newList = new CoarseList<T>() ;
      Node<T> curr = head.next ;
      while (curr != tail) {
	  newList.add(curr.item) ;
	  curr = curr.next ;
      }
      return newList ;
  }

  public String toString() {
      Node curr = head.next ;
      String s = "{" ;
      while (curr != tail) {
	  // System.out.println("curr = " + Integer.toString(curr.key) ) ;
	  s = s + curr.item.toString() ;
	  if (curr.next != tail) 
	      s = s + ", " ;
	  curr = curr.next ;
      }
      s = s + "}" ;
      return s ;
  }
  
  public boolean add(T item) {
    Node pred, curr;
    int key = item.hashCode();
    lock.lock();
    try {
      pred = head;
      curr = pred.next;
      while (curr.key < key) {
        pred = curr;
        curr = curr.next;
      }
      if (key == curr.key) {
        return false;
      } else {
        Node node = new Node<T>(item);
        node.next = curr;
        pred.next = node;
        return true;
      }
    } finally {
      lock.unlock();
    }
  }

  public boolean remove(T item) {
    Node pred, curr;
    int key = item.hashCode();
    lock.lock();
    try {
      pred = this.head;
      curr = pred.next;
      while (curr.key < key) {
        pred = curr;
        curr = curr.next;
      }
      if (key == curr.key) {  // present
        pred.next = curr.next;
        return true;
      } else {
        return false;         // not present
      }
    } finally {               // always unlock
      lock.unlock();
    }
  }

  public boolean contains(T item) {
    Node pred, curr;
    int key = item.hashCode();
    lock.lock();
    try {
      pred = head;
      curr = pred.next;
      while (curr.key < key) {
        pred = curr;
        curr = curr.next;
      }
      return (key == curr.key);
    } finally {               // always unlock
      lock.unlock();
    }
  }
}
