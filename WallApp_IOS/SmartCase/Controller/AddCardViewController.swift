//
//  AddCardViewController.swift
//  SmartCase
//
//  Created by Squareroot on 13/07/18.
//  Copyright © 2018 Squareroot. All rights reserved.
//

import UIKit

class AddCardViewController: UIViewController {
    
    @IBOutlet weak var cardImage: UIImageView!
    @IBOutlet weak var cardNameTextField: UITextField!
    @IBOutlet weak var selectColorButton: UIButton!
    @IBOutlet weak var saveButton: UIButton!
    @IBOutlet weak var deleteButton: UIButton!
    
    var isUpdate = false
    var cardModel: CardModel?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.setUpUI()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        self.setData()
    }
    
    //MARK: - setUp UI
    
    func setUpUI() {
        let gesture = UITapGestureRecognizer(target: self, action: #selector(self.selectImageTouch))
        self.cardImage.isUserInteractionEnabled = true
        self.cardImage.addGestureRecognizer(gesture)
//        self.deleteButton.isHidden = true
        if isUpdate {
            self.cardNameTextField.text = cardModel?.cardName
//            if cardModel?.cardImage != nil {
//                self.cardImage.image = UIImage(data: cardModel!.cardImage!)
//                AppData.sharedInstance.selectedImage = UIImage(data: cardModel!.cardImage!)
//            }
//            self.selectColorButton.backgroundColor = UIColor(hexString: cardModel!.cardColor!)
//            AppData.sharedInstance.selectedColor = UIColor(hexString: cardModel!.cardColor!)
            self.saveButton.setTitle("Update", for: .normal)
//            self.deleteButton.isHidden = false
        } else {
            self.saveButton.setTitle("Save", for: .normal)
        }
        
        if cardModel?.cardImage != nil {
            self.cardImage.image = UIImage(data: cardModel!.cardImage!)
            AppData.sharedInstance.selectedImage = UIImage(data: cardModel!.cardImage!)
        }
        self.selectColorButton.backgroundColor = UIColor(hexString: cardModel!.cardColor!)
        AppData.sharedInstance.selectedColor = UIColor(hexString: cardModel!.cardColor!)
    }
    
    func setData() {
        self.cardImage.image = AppData.sharedInstance.selectedImage ?? #imageLiteral(resourceName: "camera_support")
        self.selectColorButton.backgroundColor = AppData.sharedInstance.selectedColor ?? UIColor.red
    }
    
    @objc func selectImageTouch() {
        let controller = StoryBoardHelper.getSelectImageViewController()
        controller.colorFlag = false
        self.present(controller, animated: true, completion: nil)
//        self.navigationController?.pushViewController(controller, animated: true)
    }
    
    //MARK: - Button Actions
    
    @IBAction func SaveCardTouchAction(_ sender: Any) {
        
        let cardname : String = cardNameTextField.text ?? ""
        if (cardname.trimmingCharacters(in: CharacterSet.whitespaces) == "") {
            Utility.showAlert("Error", "Please enter card name", viewController: self)
        } else if self.cardImage.image == nil {
            Utility.showAlert("Error", "Please select card image", viewController: self)
        } else if self.cardImage.image == #imageLiteral(resourceName: "camera_support") {
              Utility.showAlert("Error", "Please select card image", viewController: self)
        } else {
            if isUpdate {
                self.updateCard()
            } else {
                self.addCard()
            }
        }
    }
    
    func addCard() {
        
//        cardModel = cardModel
        cardModel!.cardName = cardNameTextField.text!
        let imageData = UIImagePNGRepresentation(self.cardImage.image!)
        cardModel!.cardImage = imageData
        if AppData.sharedInstance.selectedColor == nil {
            AppData.sharedInstance.selectedColor = UIColor.red
        }
        cardModel!.cardColor = AppData.sharedInstance.selectedColor?.toHexString()
        cardModel!.isUpdate = true
        _ = CoreDataHelper.updateCardModels(cardData: cardModel!)
         NotificationCenter.default.post(name: NotificationCenterHelper.reloadViewData, object: nil)
       self.dismiss(animated: true, completion: nil)
    }
    
    func updateCard() {
        cardModel!.cardName = cardNameTextField.text!
        let imageData = UIImagePNGRepresentation(self.cardImage.image!)
        cardModel!.cardImage = imageData
        cardModel!.cardColor = AppData.sharedInstance.selectedColor?.toHexString()
         cardModel!.isUpdate = true
        _ = CoreDataHelper.updateCardModels(cardData: cardModel!)
         NotificationCenter.default.post(name: NotificationCenterHelper.reloadViewData, object: nil)
       self.dismiss(animated: true, completion: nil)
    }
    
    @IBAction func selectColorTouchAction(_ sender: Any) {
        let controller = StoryBoardHelper.getSelectImageViewController()
        controller.colorFlag = true
        self.present(controller, animated: true, completion: nil)
//        self.navigationController?.pushViewController(controller, animated: true)
    }
    
    @IBAction func deleteTouchAction(_ sender: Any) {
        Utility.showAlert(AppName, "Are you sure you want to delete this card?", viewController: self, okButtonTitle: "Ok", true, cancelButtonTitle: "Cancel", okClicked: {
            _ = CoreDataHelper.deleteCard(index: self.cardModel!.coreObject.objectID)
            self.navigationController?.popViewController(animated: true)
        }) {
            
        }
    }
    @IBAction func closeButton(_ sender: Any) {
         self.dismiss(animated: true, completion: nil)
    }
}
