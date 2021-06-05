//
//  SerialDetailViewController.swift
//  SmartCase
//
//  Created by Squareroot on 27/07/18.
//  Copyright © 2018 Squareroot. All rights reserved.
//

import UIKit

class SerialDetailViewController: UIViewController {

    @IBOutlet weak var cardName: UILabel!
    @IBOutlet weak var cardImage: UIImageView!
    @IBOutlet weak var cardView: UIView!
    var cardModel: CardModel?
    
    override func viewDidLoad() {
        super.viewDidLoad()
         self.isSwipable()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        self.cardName.text = cardModel?.cardName
        if cardModel?.cardImage != nil {
            self.cardImage.image = UIImage(data: cardModel!.cardImage!)
        }
        self.cardView.backgroundColor = UIColor(hexString: cardModel!.cardColor!)//UIColor.white
//        self.view.backgroundColor =  UIColor(hexString: cardModel!.cardColor!)
    }
    
    @IBAction func backButton(_ sender: Any) {
        NotificationCenter.default.post(name: NotificationCenterHelper.SendDimissView, object: nil)
        self.dismiss(animated: true, completion: nil)
    }
    
    func isSwipable() {
        
        var panGesture = UIPanGestureRecognizer()
        panGesture = UIPanGestureRecognizer(target: self, action: #selector(self.draggedView(_:)))
        cardView.isUserInteractionEnabled = true
        cardView.addGestureRecognizer(panGesture)
       
    }
    
    @objc func draggedView(_ sender:UIPanGestureRecognizer){
        self.view.bringSubview(toFront: cardView)
        let translation = sender.translation(in: self.view)
        cardView.center = CGPoint(x: cardView.center.x + translation.x, y: cardView.center.y + translation.y)
        
        let percentThreshold:CGFloat = 0.3
//        let translation = sender.translation(in: view)
        
        let newX = ensureRange(value: view.frame.minX + translation.x, minimum: 0, maximum: view.frame.maxX)
        let progress = progressAlongAxis(newX, view.bounds.width)
        
        if sender.state == .ended {
            let velocity = sender.velocity(in: view)
            if velocity.y >= 300 || progress > percentThreshold {
                self.dismiss(animated: true) //Perform dismiss
                
                   NotificationCenter.default.post(name: NotificationCenterHelper.SendDimissView, object: nil)
                
            } else {
                UIView.animate(withDuration: 0.2, animations: {
                    self.view.frame.origin.x = 0 // Revert animation
                })
            }
        }
        
//        if (self.cardView.frame.origin.y >= -(self.view.frame.size.height/2)) {
//             self.dismiss(animated: true, completion: nil)
//        }
        sender.setTranslation(CGPoint.zero, in: self.view)
    }
    
    func progressAlongAxis(_ pointOnAxis: CGFloat, _ axisLength: CGFloat) -> CGFloat {
        let movementOnAxis = pointOnAxis / axisLength
        let positiveMovementOnAxis = fmaxf(Float(movementOnAxis), 0.0)
        let positiveMovementOnAxisPercent = fminf(positiveMovementOnAxis, 1.0)
        return CGFloat(positiveMovementOnAxisPercent)
    }
    
    func ensureRange<T>(value: T, minimum: T, maximum: T) -> T where T : Comparable {
        return min(max(value, minimum), maximum)
    }
}
