//
//  SelectImageViewController.swift
//  SmartCase
//
//  Created by Squareroot on 13/07/18.
//  Copyright © 2018 Squareroot. All rights reserved.
//

import UIKit

class SelectImageViewController: UIViewController, UICollectionViewDelegate, UICollectionViewDataSource {
    
    @IBOutlet weak var collectionView: UICollectionView!
    var cardImageList: [UIImage] = []
    var cardColorList: [UIColor] = []
    var colorFlag: Bool = false
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.cardImageList = [#imageLiteral(resourceName: "credit-card"),#imageLiteral(resourceName: "ic_ID"),#imageLiteral(resourceName: "ic_health"),#imageLiteral(resourceName: "ic_AAA"),#imageLiteral(resourceName: "gift-box-with-a-ribbon"),#imageLiteral(resourceName: "shield"),#imageLiteral(resourceName: "LogoMakr_49NIE7")]
        self.cardColorList = [ UIColor(hexString: redColor), UIColor(hexString: orangeColor), UIColor(hexString: yellowColor), UIColor(hexString: greenColor), UIColor(hexString: tealBlueColor), UIColor(hexString: purpleColor), UIColor(hexString: pinkColor), UIColor.white] as! [UIColor]
    }
    
    @IBAction func closeButton(_ sender: Any) {
        self.dismiss(animated: true, completion: nil)
    }
    //MARK: - UICollectionView Delegate & Datasource
    
    func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        if colorFlag {
            return self.cardColorList.count
        } else {
            return self.cardImageList.count
        }
    }
    
    func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
        let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "Cell", for: indexPath) as! SerialCollectionViewCell
        
        if colorFlag {
            cell.cardImage.image = UIImage(named: "")
            cell.cardImage.backgroundColor = self.cardColorList[indexPath.item]
        } else {
            cell.cardImage.image = self.cardImageList[indexPath.item]
            cell.cardImage.backgroundColor = UIColor.clear
        }
        
        return cell
    }
    
    func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
        if colorFlag {
            let selectedColor =   self.cardColorList[indexPath.item]
            AppData.sharedInstance.selectedColor = selectedColor
        } else {
            let selectedImage =   self.cardImageList[indexPath.item]
            AppData.sharedInstance.selectedImage = selectedImage
        }
        self.dismiss(animated: true, completion: nil)
        //        self.navigationController?.popViewController(animated: true)
    }
    
}
