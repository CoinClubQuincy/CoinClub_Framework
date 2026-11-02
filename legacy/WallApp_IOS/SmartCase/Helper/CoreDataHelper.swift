//
//  CoreDataHelper.swift
//  MoneyManager
//
//  Created by KMSOFT on 16/04/18.
//  Copyright © 2018 KMSOFT. All rights reserved.
//

import UIKit
import CoreData
import Foundation

class CoreDataHelper {
    
    // Mark :- Account
    
    class func getCards() -> [CardModel] {
        var CardModels = CoreDataHelper.getCardModels()
        if CardModels.count == 0 {
            CardModels = CoreDataHelper.saveDefaultCardModels()
        }
        return CardModels
    }
    
    fileprivate class func getCardModels() -> [CardModel] {
        let context = Utility.getContext()
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "Card")
        request.returnsObjectsAsFaults = false
        
        var CardModels: [CardModel] = []
        
        do {
            let result = try context.fetch(request)
            
            for data in result as! [Card] {
                let cardModel = CardModel()
                cardModel.cardName = data.cardName
                cardModel.cardColor = data.cardColor
                cardModel.cardImage = data.cardImage as? Data ?? nil
                cardModel.isUpdate = data.isUpdate
                cardModel.coreObject = data
                CardModels.append(cardModel)
            }
            
            
        } catch let error {
            print(error.localizedDescription)
        }
        return CardModels
    }
    
    fileprivate static func saveDefaultCardModels() -> [CardModel] {
        //        let cardNameList = ["Credit Card","Debit Card","ID","Health Insurance","AAA","Empty"]
        let cardNameList = ["Press to add slot","Press to add slot","Press to add slot","Press to add slot","Press to add slot","Press to add slot"]
        //        var cardImages : [UIImage] = [#imageLiteral(resourceName: "credit-card"),#imageLiteral(resourceName: "credit-card"),#imageLiteral(resourceName: "ic_ID"),#imageLiteral(resourceName: "ic_health"),#imageLiteral(resourceName: "car-front"),UIImage()]
        
        var cardImages : [UIImage] = [#imageLiteral(resourceName: "add"),#imageLiteral(resourceName: "add"),#imageLiteral(resourceName: "add"),#imageLiteral(resourceName: "add"),#imageLiteral(resourceName: "add"),#imageLiteral(resourceName: "add")]
        
        var cardColor : [String] = [redColor,orangeColor,yellowColor,greenColor,tealBlueColor,purpleColor]
        
        for i in 0 ..< cardNameList.count {
            let context = Utility.getContext()
            let entity = NSEntityDescription.entity(forEntityName: "Card", in: context)
            let newCard = NSManagedObject(entity: entity!, insertInto: context)
            newCard.setValue(cardNameList[i], forKey: "cardName")
            newCard.setValue(UIImagePNGRepresentation(cardImages[i]), forKey: "cardImage")
            newCard.setValue(cardColor[i], forKey: "cardColor")
            newCard.setValue(false, forKey: "isUpdate")
            do {
                try context.save()
            } catch let error {
                print(error.localizedDescription)
            }
        }
        return CoreDataHelper.getCards()
    }
    
    static func saveCardModels(cardData : CardModel) -> [CardModel] {
        
        let context = Utility.getContext()
        
        let entity = NSEntityDescription.entity(forEntityName: "Card", in: context)
        let newCard = NSManagedObject(entity: entity!, insertInto: context)
        
        newCard.setValue(cardData.cardName, forKey: "cardName")
        newCard.setValue(cardData.cardImage, forKey: "cardImage")
        newCard.setValue(cardData.cardColor, forKey: "cardColor")
        newCard.setValue(cardData.isUpdate, forKey: "isUpdate")
        do {
            try context.save()
        } catch let error {
            print(error.localizedDescription)
        }
        return CoreDataHelper.getCards()
    }
    
    static func updateCardModels(cardData : CardModel) -> [CardModel] {
        
        let context = Utility.getContext()
        if let managedObject = try? context.existingObject(with: cardData.coreObject.objectID) {
            managedObject.setValue(cardData.cardName, forKey: "cardName")
            managedObject.setValue(cardData.cardImage, forKey: "cardImage")
            managedObject.setValue(cardData.cardColor, forKey: "cardColor")
            managedObject.setValue(cardData.isUpdate, forKey: "isUpdate")
            do {
                try context.save()
            } catch let error {
                print(error.localizedDescription)
            }
        }
        return CoreDataHelper.getCards()
    }
    
    static func deleteCard(index : NSManagedObjectID) -> [CardModel] {
        
        let context = Utility.getContext()
        if let managedObject = try? context.existingObject(with: index) {
            context.delete(managedObject)
            do {
                try context.save()
            } catch let error {
                print(error.localizedDescription)
            }
        }
        return CoreDataHelper.getCards()
    }
    
}
