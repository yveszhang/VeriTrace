/*
 * FineList.java
 *
 * Created on January 3, 2006, 6:50 PM
 *
 * From "Multiprocessor Synchronization and Concurrent Data Structures",
 * by Maurice Herlihy and Nir Shavit.
 * Copyright 2006 Elsevier Inc. All rights reserved.
 */
package concurrency ;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class FineList<T> {
  private Node head;
  public FineList() {
    // Add sentinels to start and end
    head      = new Node(Integer.MIN_VALUE);
    head.next = new Node(Integer.MAX_VALUE);
  }

  public FineList<T> clone() {
      FineList<T> l = new FineList<T>() ;
      Node curr = head.next ;
      while (curr.key < Integer.MAX_VALUE) {
	  l.add(curr.item) ;
	  curr = curr.next ;
      }
      return l ;
  }

  public String toString() {
      String s = "{" ;
      Node curr = head.next ;
      while (curr.key < Integer.MAX_VALUE) {
	  s = s + curr.item.toString() ;
	  curr = curr.next ;
	  if (curr.key < Integer.MAX_VALUE) 
	      s = s + ", " ;
      }
      s = s + "}" ;
      return s ;
  }

  public boolean add(T item) {
    int key = item.hashCode();
    head.lock();
    Node pred = head;
    try {
      Node curr = pred.next;
      curr.lock();
      try {
        while (curr.key < key) {
          pred.unlock();
          pred = curr;
          curr = curr.next;
          curr.lock();
        }
        if (curr.key == key) {
          return false;
        }
        Node newNode = new Node(item);
        newNode.next = curr;
        pred.next = newNode;
        return true;
      } finally {
        curr.unlock();
      }
    } finally {
      pred.unlock();
    }
  }

  public boolean remove(T item) {
    Node pred = null, curr = null;
    int key = item.hashCode();
    head.lock();
    try {
      pred = head;
      curr = pred.next;
      curr.lock();
      try {
        while (curr.key < key) {
          pred.unlock();
          pred = curr;
          curr = curr.next;
          curr.lock();
        }
        if (curr.key == key) {
          pred.next = curr.next;
          return true;
        }
        return false;
      } finally {
        curr.unlock();
      }
    } finally {
      pred.unlock();
    }
  }
  public boolean contains(T item) {
    Node last = null, pred = null, curr = null;
    int key = item.hashCode();
    head.lock();
    try {
      pred = head;
      curr = pred.next;
      curr.lock();
      try {
        while (curr.key < key) {
          pred.unlock();
          pred = curr;
          curr = curr.next;
          curr.lock();
        }
        return (curr.key == key);
      } finally {
        curr.unlock();
      }
    } finally {
      pred.unlock();
    }
  }

  private class Node {
    T item;
    int key;
    Node next;
    Lock lock;
    Node(T item) {
      this.item = item;
      this.key = item.hashCode();
      this.lock = new ReentrantLock();
    }
    Node(int key) {
      this.item = null;
      this.key = key;
      this.lock = new ReentrantLock();
    }
    void lock() {lock.lock();}
    void unlock() {lock.unlock();}
  }
}

